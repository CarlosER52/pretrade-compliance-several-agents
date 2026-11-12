"""Acciones deterministas de las transiciones de la red de Petri.

Cada función recibe `context` (dict con los datos de la orden y artefactos
previos) y `places` (dict con los Place de la red, para leer/escribir
tokens si hace falta). Devuelve un dict con el resultado de la acción,
que el motor usa para poblar los places de salida.

Regla de diseño: estas acciones son deterministas y no llaman al LLM.
Las acciones que sí llaman al LLM viven en `src/agents/`.
"""

import hashlib
import json
from typing import Any

from src.schemas import (
    AnalisisContexto,
    ClasificacionRiesgo,
    ReglaResultado,
    ValidacionReglas,
)


# ------------------------------------------------------------
# Utilidades
# ------------------------------------------------------------

def calcular_hash(payload: Any) -> str:
    """Hash sha256 estable de un payload (dict, str o bytes)."""
    if isinstance(payload, bytes):
        data = payload
    elif isinstance(payload, str):
        data = payload.encode("utf-8")
    else:
        data = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _as_dict(obj: Any) -> dict:
    """Convierte un modelo Pydantic o dict a dict plano."""
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if isinstance(obj, dict):
        return obj
    return dict(obj)


# ------------------------------------------------------------
# t_validar_schema -> schema_guard + acción
# ------------------------------------------------------------

def validar_schema_action(context: dict, places: dict) -> dict:
    """Valida el schema de la orden entrante.

    Requiere en `context`:
        - `orden`: dict con los campos de la orden.

    Devuelve:
        - `{"ok": True, "orden": orden}` si es válida.
        - `{"ok": False, "error": {...}}` si no lo es.
    """
    orden = context.get("orden")
    if orden is None:
        return {"ok": False, "error": {"tipo_error": "orden_ausente"}}

    requeridos = ["orden_id", "instrumento", "tipo", "cantidad",
                  "cuenta_id", "cliente_id"]
    faltantes = [k for k in requeridos if k not in orden]
    if faltantes:
        return {
            "ok": False,
            "error": {
                "tipo_error": "campos_faltantes",
                "detalle": f"Faltan: {faltantes}",
                "orden_original": orden,
            },
        }

    if orden["instrumento"] not in ("stocks", "forex", "crypto", "futures", "options"):
        return {
            "ok": False,
            "error": {
                "tipo_error": "instrumento_invalido",
                "detalle": orden["instrumento"],
                "orden_original": orden,
            },
        }

    if orden["tipo"] not in ("buy", "sell"):
        return {
            "ok": False,
            "error": {
                "tipo_error": "tipo_invalido",
                "detalle": orden["tipo"],
                "orden_original": orden,
            },
        }

    if orden.get("cantidad", 0) <= 0:
        return {
            "ok": False,
            "error": {
                "tipo_error": "cantidad_invalida",
                "detalle": orden["cantidad"],
                "orden_original": orden,
            },
        }

    return {"ok": True, "orden": orden}


# ------------------------------------------------------------
# t_ejecutar_reglas -> ejecuta las reglas duras del instrumento
# ------------------------------------------------------------

def ejecutar_reglas_action(context: dict, places: dict) -> dict:
    """Ejecuta las reglas duras correspondientes al instrumento.

    Requiere en `context`:
        - `orden`: dict (ya validado).
        - `contexto_cliente`: dict con datos del cliente (capital, posición, etc.).

    Devuelve un `ValidacionReglas` serializado como dict.
    """
    from src.rules.registry import ejecutar_reglas_por_instrumento

    orden = context["orden"]
    contexto_cliente = context.get("contexto_cliente", {})

    resultados = ejecutar_reglas_por_instrumento(orden, contexto_cliente)

    fallos = sum(1 for r in resultados if r.resultado == "fail")

    validacion = ValidacionReglas(
        orden_id=orden["orden_id"],
        instrumento=orden["instrumento"],
        reglas=[r.model_dump() for r in resultados],
        fallos_total=fallos,
        hash_inputs=calcular_hash(orden),
    )
    return validacion.model_dump()


# ------------------------------------------------------------
# t_clasificar_con_piso -> aplica el piso de reglas duras
# ------------------------------------------------------------

def clasificar_con_piso_action(context: dict, places: dict) -> dict:
    """Clasifica el riesgo aplicando el piso de reglas duras.

    Requiere en `context`:
        - `validacion`: dict del artefacto ValidacionReglas.
        - `analisis`: dict del artefacto AnalisisContexto.
        - `riesgo_sugerido_por_agente`: str (LOW/MEDIUM/HIGH/CRITICAL).

    Devuelve un `ClasificacionRiesgo` serializado como dict.

    Regla de oro: si `validacion.fallos_total > 0`, el riesgo resultante
    DEBE ser al menos HIGH, sin importar lo que diga el agente.
    """
    validacion = _as_dict(context["validacion"])
    analisis = _as_dict(context["analisis"])
    riesgo_agente = context.get("riesgo_sugerido_por_agente", "LOW")

    piso_aplicado = False
    riesgo_final = riesgo_agente

    # Piso: si hay fallos, mínimo HIGH
    if validacion["fallos_total"] > 0:
        if riesgo_agente in ("LOW", "MEDIUM"):
            piso_aplicado = True
            riesgo_final = "HIGH"

    # Coherencia con watchlist: si está en watchlist, no puede ser LOW
    if analisis.get("cliente_en_watchlist") and riesgo_final == "LOW":
        piso_aplicado = True
        riesgo_final = "MEDIUM"

    justificacion = (
        f"Riesgo base sugerido por agente: {riesgo_agente}. "
        f"Fallos en reglas duras: {validacion['fallos_total']}. "
        f"Piso aplicado: {piso_aplicado}."
    )

    clasificacion = ClasificacionRiesgo(
        orden_id=validacion["orden_id"],
        riesgo=riesgo_final,
        justificacion=justificacion,
        piso_aplicado=piso_aplicado,
        riesgo_sugerido_por_agente=riesgo_agente,
        hash_inputs=validacion["hash_inputs"],
    )
    return clasificacion.model_dump()


# ------------------------------------------------------------
# t_timeout_analisis -> saca la orden a p_error
# ------------------------------------------------------------

def timeout_analisis_action(context: dict, places: dict) -> dict:
    """Registra el timeout de análisis y produce un error.

    Requiere en `context`:
        - `orden`: dict.
        - `sla_segundos`: int (opcional, para el detalle).
    """
    orden = context.get("orden", {})
    return {
        "tipo_error": "timeout_analisis",
        "detalle": (
            f"La orden {orden.get('orden_id')} excedió el SLA de análisis "
            f"({context.get('sla_segundos', 'N/A')}s) sin liberar el pool."
        ),
        "orden_original": orden,
    }


# ------------------------------------------------------------
# t_recargar_budget -> devuelve tokens a p_api_budget
# ------------------------------------------------------------

def recargar_budget_action(context: dict, places: dict) -> dict:
    """Recarga el presupuesto de API.

    Esta acción no produce un artefacto: su efecto es devolver tokens
    al place `p_api_budget`. El motor de la red es quien debe rellenar
    el place; aquí solo dejamos constancia en el contexto.
    """
    return {
        "evento": "recarga_budget",
        "tokens_recargados": context.get("tokens_recargar", 10),
        "ventana": context.get("ventana_id"),
    }