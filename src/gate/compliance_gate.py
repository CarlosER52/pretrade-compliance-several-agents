"""Gate humano de compliance.

Modela las transiciones t_aprobar y t_rechazar de la red de Petri.
El oficial de compliance decide, pero las guardas deterministas
verifican que la decisión es válida antes de producir el acta.

Regla de oro: el oficial puede aprobar una orden que viola una regla
dura SOLO si documenta una excepción (justificación >= 20 caracteres).
Eso queda en el acta y es auditable.
"""

from datetime import datetime

from src.schemas import ActaCompliance, ClasificacionRiesgo


# ------------------------------------------------------------
# Guardas del gate
# ------------------------------------------------------------

def validar_aprobacion(context: dict, places: dict) -> tuple[bool, str]:
    """Guarda de t_aprobar.

    Requiere en context:
        - `clasificacion`: ClasificacionRiesgo (o dict).
        - `oficial`: str (id del oficial).
        - `firma`: str (firma digital).
        - `justificacion`: str (obligatoria si piso_aplicado).
        - `agente_origen`: str (id del agente que analizó, para evitar
          conflicto de interés).
    """
    clasificacion = context.get("clasificacion")
    oficial = context.get("oficial")
    firma = context.get("firma")
    justificacion = context.get("justificacion", "")
    agente_origen = context.get("agente_origen", "analyst_agent")

    if not clasificacion:
        return False, "clasificacion_ausente"
    if not oficial:
        return False, "oficial_ausente"
    if not firma:
        return False, "firma_ausente"

    # Conflicto de interés: el oficial no puede ser el agente
    if oficial == agente_origen:
        return False, "conflicto_interes:oficial==agente"

    # Si el piso se aplicó (reglas duras fallaron), la aprobación
    # requiere justificación documentada
    piso_aplicado = (
        clasificacion.get("piso_aplicado")
        if isinstance(clasificacion, dict)
        else clasificacion.piso_aplicado
    )
    if piso_aplicado and len(justificacion) < 20:
        return False, "aprobacion_con_piso_requiere_justificacion"

    # Rechazo siempre requiere justificación
    # (esto se valida en validar_rechazo, no aquí)

    return True, "OK"


def validar_rechazo(context: dict, places: dict) -> tuple[bool, str]:
    """Guarda de t_rechazar.

    Requiere en context:
        - `clasificacion`: ClasificacionRiesgo (o dict).
        - `oficial`: str.
        - `firma`: str.
        - `justificacion`: str (>= 20 caracteres, obligatoria).
    """
    clasificacion = context.get("clasificacion")
    oficial = context.get("oficial")
    firma = context.get("firma")
    justificacion = context.get("justificacion", "")

    if not clasificacion:
        return False, "clasificacion_ausente"
    if not oficial:
        return False, "oficial_ausente"
    if not firma:
        return False, "firma_ausente"
    if len(justificacion) < 20:
        return False, "rechazo_requiere_justificacion_20_chars"

    return True, "OK"


# ------------------------------------------------------------
# Acciones de las transiciones
# ------------------------------------------------------------

def aprobar_action(context: dict, places: dict) -> dict:
    """Acción de t_aprobar. Produce el ActaCompliance (aprobada)."""
    clasificacion = _as_clasificacion(context["clasificacion"])

    acta = ActaCompliance(
        orden_id=clasificacion.orden_id,
        decision="aprobada",
        oficial=context["oficial"],
        firma=context["firma"],
        timestamp=datetime.utcnow(),
        justificacion=context.get("justificacion") or (
            "Aprobación sin excepción documentada."
        ),
        hash_clasificacion=clasificacion.hash_inputs,
    )
    return acta.model_dump()


def rechazar_action(context: dict, places: dict) -> dict:
    """Acción de t_rechazar. Produce el ActaCompliance (rechazada)."""
    clasificacion = _as_clasificacion(context["clasificacion"])

    acta = ActaCompliance(
        orden_id=clasificacion.orden_id,
        decision="rechazada",
        oficial=context["oficial"],
        firma=context["firma"],
        timestamp=datetime.utcnow(),
        justificacion=context["justificacion"],
        hash_clasificacion=clasificacion.hash_inputs,
    )
    return acta.model_dump()


def enqueue_action(context: dict, places: dict) -> dict:
    """Acción de t_enviar_a_gate. Encola la orden para revisión humana."""
    clasificacion = _as_clasificacion(context["clasificacion"])
    return {
        "orden_id": clasificacion.orden_id,
        "riesgo": clasificacion.riesgo,
        "piso_aplicado": clasificacion.piso_aplicado,
        "en_cola_desde": datetime.utcnow().isoformat(),
        "clasificacion": clasificacion.model_dump(),
    }


# ------------------------------------------------------------
# Utilidades
# ------------------------------------------------------------

def _as_clasificacion(obj) -> ClasificacionRiesgo:
    """Acepta ClasificacionRiesgo o dict y devuelve ClasificacionRiesgo."""
    if isinstance(obj, ClasificacionRiesgo):
        return obj
    return ClasificacionRiesgo(**obj)