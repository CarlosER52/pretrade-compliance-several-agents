"""Demo de Pre-Trade Compliance Agent con visualización de red de Petri.

Flujo:
1. Selector de instrumento + formulario de orden.
2. Al enviar: schema -> reglas -> analista -> clasificación con piso.
3. Visualización de la red con Mermaid (estado actual resaltado).
4. Artefactos generados (JSONs).
5. Gate humano (aprobar/rechazar) si el riesgo >= MEDIUM.
"""

import json
import sys
from pathlib import Path

import streamlit as st

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.agents.analyst import analyst_agent_action
# Después de clasificar, antes del gate
from src.agents.writer import writer_agent_action
from src.gate.compliance_gate import aprobar_action, rechazar_action
from src.petri.transitions import (
    clasificar_con_piso_action,
    ejecutar_reglas_action,
    validar_schema_action,
)
from src.archive.audit_trail import archivar_action, validar_archivo
# ============================================================
# Configuración de página
# ============================================================

st.set_page_config(
    page_title="Pre-Trade Compliance Agent",
    page_icon="🛡️",
    layout="wide",
)

# ============================================================
# Estado de sesión
# ============================================================

if "resultado" not in st.session_state:
    st.session_state.resultado = None
if "acta" not in st.session_state:
    st.session_state.acta = None
if "instrumento_actual" not in st.session_state:
    st.session_state.instrumento_actual = "stocks"


# ============================================================
# Formularios por instrumento
# ============================================================

def formulario_stocks():
    st.subheader("Orden de Stocks")
    col1, col2, col3 = st.columns(3)
    with col1:
        orden_id = st.text_input("Orden ID", value="ORD-2026-11-00001", key="st_oid")
        simbolo = st.text_input("Símbolo", value="TSLA", key="st_sym")
        cantidad = st.number_input("Cantidad", min_value=1, value=1000, key="st_qty")
    with col2:
        precio = st.number_input("Precio (0 = market)", min_value=0.0, value=200.0, step=1.0, key="st_px")
        sector = st.text_input("Sector", value="tech", key="st_sec")
        tipo = st.selectbox("Tipo", ["buy", "sell"], key="st_tipo")
    with col3:
        capital = st.number_input("Capital cuenta", min_value=1000.0, value=1_500_000.0, step=1000.0, key="st_cap")
        posicion_actual = st.number_input("Posición actual", min_value=0.0, value=0.0, step=1.0, key="st_pos")
        en_watchlist = st.checkbox("Cliente en watchlist", value=False, key="st_wl")

    return {
        "orden": {
            "orden_id": orden_id, "instrumento": "stocks", "tipo": tipo,
            "cantidad": cantidad, "simbolo": simbolo,
            "precio": precio if precio > 0 else None,
            "tipo_orden": "limit" if precio > 0 else "market",
            "cuenta_id": "ACC-4471", "cliente_id": "CLI-001", "sector": sector,
        },
        "contexto": {
            "capital_cuenta": capital,
            "posicion_actual": {simbolo: posicion_actual},
            "exposicion_sector": {sector: 0},
            "precio_referencia": {simbolo: precio if precio > 0 else 200},
            "contra_partida_cliente_id": None,
            "cliente_en_watchlist": en_watchlist,
        },
    }


def formulario_forex():
    st.subheader("Orden de Forex")
    col1, col2, col3 = st.columns(3)
    with col1:
        orden_id = st.text_input("Orden ID", value="ORD-2026-11-00002", key="fx_oid")
        par = st.text_input("Par", value="EUR/USD", key="fx_par")
        cantidad = st.number_input("Cantidad", min_value=1.0, value=10000.0, step=1000.0, key="fx_qty")
    with col2:
        tasa = st.number_input("Tasa", min_value=0.0, value=1.08, step=0.01, key="fx_rate")
        jurisdiccion = st.selectbox("Jurisdicción", ["EU", "US", "UK", "JP", "IR", "KP"], key="fx_jur")
        contraparte = st.selectbox("Contraparte", ["BANK_A", "BANK_B", "BANK_Z"], key="fx_cp")
    with col3:
        capital = st.number_input("Capital cuenta", min_value=1000.0, value=1_000_000.0, step=1000.0, key="fx_cap")
        timestamp = st.text_input("Timestamp (UTC)", value="2026-11-10T10:00:00", key="fx_ts")

    return {
        "orden": {
            "orden_id": orden_id, "instrumento": "forex", "tipo": "buy",
            "cantidad": cantidad, "par": par, "tasa": tasa,
            "cuenta_id": "ACC-4472", "cliente_id": "CLI-002",
            "jurisdiccion_cliente": jurisdiccion, "timestamp": timestamp,
        },
        "contexto": {
            "capital_cuenta": capital, "exposicion_par": {},
            "tasa_referencia": {par: tasa},
            "jurisdiccion_cliente": jurisdiccion, "contraparte": contraparte,
        },
    }


def formulario_crypto():
    st.subheader("Orden de Crypto")
    col1, col2, col3 = st.columns(3)
    with col1:
        orden_id = st.text_input("Orden ID", value="ORD-2026-11-00003", key="cr_oid")
        token = st.text_input("Token", value="BTC", key="cr_tok")
        cantidad = st.number_input("Cantidad", min_value=0.01, value=1.5, step=0.1, key="cr_qty")
    with col2:
        precio = st.number_input("Precio", min_value=0.0, value=60000.0, step=100.0, key="cr_px")
        exchange = st.selectbox("Exchange", ["BINANCE", "COINBASE", "KRAKEN"], key="cr_ex")
        jurisdiccion = st.selectbox("Jurisdicción", ["EU", "US", "SG", "CN"], key="cr_jur")
    with col3:
        capital = st.number_input("Capital cuenta", min_value=1000.0, value=1_000_000.0, step=1000.0, key="cr_cap")

    return {
        "orden": {
            "orden_id": orden_id, "instrumento": "crypto", "tipo": "buy",
            "cantidad": cantidad, "token": token, "exchange": exchange,
            "precio": precio, "cuenta_id": "ACC-4473", "cliente_id": "CLI-003",
            "jurisdiccion_cliente": jurisdiccion,
        },
        "contexto": {
            "capital_cuenta": capital, "exposicion_exchange": {},
            "precio_referencia": {token: precio}, "jurisdiccion_cliente": jurisdiccion,
        },
    }


def formulario_futures():
    st.subheader("Orden de Futures")
    col1, col2, col3 = st.columns(3)
    with col1:
        orden_id = st.text_input("Orden ID", value="ORD-2026-11-00004", key="fu_oid")
        contrato = st.text_input("Contrato", value="ESZ6", key="fu_con")
        cantidad = st.number_input("Cantidad (contratos)", min_value=1, value=10, key="fu_qty")
    with col2:
        vencimiento = st.text_input("Vencimiento", value="2026-12-18", key="fu_ven")
        margen = st.number_input("Margen disponible", min_value=0.0, value=500_000.0, step=10000.0, key="fu_marg")
        timestamp = st.text_input("Timestamp (UTC)", value="2026-11-10T15:00:00", key="fu_ts")
    with col3:
        es_roll = st.checkbox("Es roll", value=False, key="fu_roll")

    return {
        "orden": {
            "orden_id": orden_id, "instrumento": "futures", "tipo": "buy",
            "cantidad": cantidad, "contrato": contrato,
            "vencimiento": vencimiento, "margen_disponible": margen,
            "precio": 4500, "cuenta_id": "ACC-4474", "cliente_id": "CLI-004",
            "timestamp": timestamp,
        },
        "contexto": {"posicion_vencimiento": {}, "es_roll": es_roll},
    }


def formulario_options():
    st.subheader("Orden de Options")
    col1, col2, col3 = st.columns(3)
    with col1:
        orden_id = st.text_input("Orden ID", value="ORD-2026-11-00005", key="op_oid")
        subyacente = st.text_input("Subyacente", value="AAPL", key="op_sub")
        cantidad = st.number_input("Cantidad", min_value=1, value=10, key="op_qty")
    with col2:
        tipo_opcion = st.selectbox("Tipo opción", ["call", "put"], key="op_tipo")
        strike = st.number_input("Strike", min_value=0.0, value=180.0, step=1.0, key="op_strike")
        vencimiento = st.text_input("Vencimiento", value="2027-01-15", key="op_ven")
    with col3:
        nivel = st.selectbox("Nivel cliente", [1, 2, 3, 4, 5], index=1, key="op_nivel")
        estrategia = st.selectbox("Estrategia", ["covered", "spread", "naked"], key="op_est")
        delta_orden = st.number_input("Delta orden", value=50.0, step=10.0, key="op_delta")

    return {
        "orden": {
            "orden_id": orden_id, "instrumento": "options", "tipo": "buy",
            "cantidad": cantidad, "subyacente": subyacente,
            "tipo_opcion": tipo_opcion, "strike": strike,
            "vencimiento": vencimiento, "nivel_aprobacion_cliente": nivel,
            "estrategia": estrategia, "cuenta_id": "ACC-4475", "cliente_id": "CLI-005",
        },
        "contexto": {"delta_total": 100.0, "delta_orden": delta_orden},
    }


# ============================================================
# Visualización de la red de Petri con Mermaid
# ============================================================

def render_red_petri(estado_actual: str | None = None):
    """Dibuja la red de Petri con Mermaid, resaltando el estado actual."""
    # Estilos por estado
    estilos = {
        "p_orden_raw": "fill:#f9f,stroke:#333,stroke-width:2px",
        "p_orden_schema_ok": "fill:#bbf,stroke:#333,stroke-width:2px",
        "p_validacion_reglas": "fill:#bbf,stroke:#333,stroke-width:2px",
        "p_analisis_contexto": "fill:#bbf,stroke:#333,stroke-width:2px",
        "p_clasificacion_riesgo": "fill:#bbf,stroke:#333,stroke-width:2px",
        "p_cola_gate": "fill:#fbb,stroke:#333,stroke-width:3px",
        "p_acta_compliance": "fill:#bfb,stroke:#333,stroke-width:2px",
        "p_archivada": "fill:#dfd,stroke:#333,stroke-width:2px",
        "p_error": "fill:#fdd,stroke:#333,stroke-width:2px",
    }

    if estado_actual and estado_actual in estilos:
        estilos[estado_actual] = "fill:#ffd700,stroke:#333,stroke-width:4px"

    style_lines = "\n".join(
        f"style {pid} {style}" for pid, style in estilos.items()
    )

    mermaid_code = f"""
graph TD
    A[p_orden_raw] -->|t_validar_schema| B[p_orden_schema_ok]
    B -->|t_ejecutar_reglas| C[p_validacion_reglas]
    C -->|t_ejecutar_analisis| D[p_analisis_contexto]
    D -->|t_clasificar_con_piso| E[p_clasificacion_riesgo]
    E -->|t_enviar_a_gate| F[p_cola_gate]
    F -->|t_aprobar/rechazar| G[p_acta_compliance]
    G -->|t_archivar| H[p_archivada]
    B -->|schema inválido| I[p_error]

    {style_lines}
    """
    st.mermaid_chart(mermaid_code, alt="Red de Petri del flujo de compliance")


# ============================================================
# Lógica de ejecución
# ============================================================

def ejecutar_flujo(datos: dict):
    orden = datos["orden"]
    contexto = datos["contexto"]
    instrumento = orden["instrumento"]

    # 1. Schema
    schema = validar_schema_action({"orden": orden}, {})
    if not schema["ok"]:
        return {"error": "schema", "detalle": schema["error"], "estado": "p_error"}

    # 2. Reglas
    validacion = ejecutar_reglas_action(
        {"orden": orden, "contexto_cliente": contexto}, {}
    )
    estado = "p_validacion_reglas"

    # 3. Analista (LLM o mock)
    try:
        analisis = analyst_agent_action(
            {"orden": orden, "validacion": validacion,
             "contexto_cliente": contexto}, {}
        )
    except Exception as e:
        analisis = {
            "orden_id": orden["orden_id"],
            "cliente_en_watchlist": contexto.get("cliente_en_watchlist", False),
            "patron_inusual": False, "conflicto_politica": False,
            "justificacion": f"Fallback: agente falló ({e})",
            "confianza": 0.5, "hash_inputs": validacion["hash_inputs"],
        }
    estado = "p_analisis_contexto"

    # 4. Clasificación con piso
    clasificacion = clasificar_con_piso_action(
        {"validacion": validacion, "analisis": analisis,
         "riesgo_sugerido_por_agente": "LOW"}, {}
    )
    estado = "p_clasificacion_riesgo"

    # 5. ¿Requiere gate?
    requiere_gate = clasificacion["riesgo"] != "LOW"
    if requiere_gate:
        estado = "p_cola_gate"

    # ... dentro de ejecutar_flujo, después de clasificacion ...
    memo = writer_agent_action({
        "orden": orden, "validacion": validacion,
        "analisis": analisis, "clasificacion": clasificacion,}, {}
    )

    return {
        "orden": orden, "contexto": contexto,
        "validacion": validacion, "analisis": analisis,
        "clasificacion": clasificacion,
        "requiere_gate": requiere_gate,
        "estado": estado,
        "instrumento": instrumento,
        "memo": memo,
    }


# ============================================================
# Main
# ============================================================

st.title("🛡️ Pre-Trade Compliance Agent")
st.caption("Validación de órdenes con reglas duras, agentes LLM y gate humano obligatorio")

with st.sidebar:
    st.header("Configuración")
    instrumento = st.selectbox(
        "Instrumento", ["stocks", "forex", "crypto", "futures", "options"],
        key="instrumento_sel",
    )
    st.divider()
    st.info(
        "**Flujo:**\n"
        "1. Schema → 2. Reglas duras → 3. Analista LLM\n"
        "4. Clasificación con piso → 5. Gate humano"
    )

# Formulario según instrumento
formularios = {
    "stocks": formulario_stocks,
    "forex": formulario_forex,
    "crypto": formulario_crypto,
    "futures": formulario_futures,
    "options": formulario_options,
}

with st.form("orden_form"):
    datos = formularios[instrumento]()
    submit = st.form_submit_button("Ejecutar Validación", type="primary")

if submit:
    with st.spinner("Ejecutando flujo de compliance..."):
        st.session_state.resultado = ejecutar_flujo(datos)
        st.session_state.acta = None

# ============================================================
# Renderizar resultados
# ============================================================

col_red, col_artefactos = st.columns([1, 1])

#with col_red:
#    st.subheader("Actividad")
#    if st.session_state.resultado:
#        render_red_petri(st.session_state.resultado.get("estado"))
#    else:
#        render_red_petri(None)

# artefactos
with col_artefactos:
    st.subheader("Artefactos Generados")
    if st.session_state.resultado:
        res = st.session_state.resultado
        if "error" in res:
            st.error(f"Error: {res['detalle']}")
        else:
            # Validación de reglas
            with st.expander("Validación de Reglas", expanded=False):
                st.json(res["validacion"])

            # Análisis de contexto
            with st.expander("Análisis de Contexto", expanded=False):
                st.json(res["analisis"])

            # Clasificación
            with st.expander("Clasificación de Riesgo", expanded=True):
                clas = res["clasificacion"]
                color = {"LOW": "green", "MEDIUM": "orange",
                         "HIGH": "red", "CRITICAL": "darkred"}.get(clas["riesgo"], "gray")
                st.markdown(f"**Riesgo:** :{color}[{clas['riesgo']}]")
                st.markdown(f"**Piso aplicado:** {clas['piso_aplicado']}")
                st.markdown(f"**Riesgo sugerido por agente:** {clas.get('riesgo_sugerido_por_agente', 'N/A')}")
                st.code(clas["justificacion"], language="text")

            # Después del expander de clasificación
            with st.expander("Memo de Compliance", expanded=True):
                st.markdown(res["memo"]["memo"])
    else:
        st.info("Completa el formulario y ejecuta la validación.")

# ============================================================
# Gate humano
# ============================================================

if st.session_state.resultado and not st.session_state.resultado.get("error"):
    res = st.session_state.resultado
    if res.get("requiere_gate"):
        st.divider()
        st.subheader("🔐 Gate Humano (Revisión Obligatoria)")
        st.warning(f"Riesgo **{res['clasificacion']['riesgo']}** requiere aprobación del oficial.")

        with st.form("gate_form"):
            oficial = st.text_input("Oficial", value="oficial_001", key="gate_oficial")
            firma = st.text_input("Firma digital", value="firma_digital_abc123", key="gate_firma")
            justificacion = st.text_area(
                "Justificación (obligatoria si piso_aplicado)",
                value="Excepción aprobada por comité de riesgos, acta #123.",
                key="gate_just",
            )
            col_a, col_r = st.columns(2)
            with col_a:
                aprobar_btn = st.form_submit_button("✅ Aprobar", type="primary")
            with col_r:
                rechazar_btn = st.form_submit_button("❌ Rechazar")

        gate_ctx = {
            "clasificacion": res["clasificacion"],
            "oficial": oficial,
            "firma": firma,
            "justificacion": justificacion,
            "agente_origen": "analyst_agent",
        }

        if aprobar_btn:
            try:
                acta = aprobar_action(gate_ctx, {})
                st.session_state.acta = acta
                st.success(f"✅ Orden **{acta['orden_id']}** aprobada por {acta['oficial']}")
            except Exception as e:
                st.error(f"Error al aprobar: {e}")

        if rechazar_btn:
            try:
                acta = rechazar_action(gate_ctx, {})
                st.session_state.acta = acta
                st.error(f"❌ Orden **{acta['orden_id']}** rechazada por {acta['oficial']}")
            except Exception as e:
                st.error(f"Error al rechazar: {e}")

    else:
        st.success(f"✅ Orden **{res['orden']['orden_id']}** clasificada como **LOW**. No requiere gate.")

# ============================================================
# Acta final
# ============================================================

if st.session_state.acta:
    st.divider()
    st.subheader("📋 Acta de Compliance (Audit Trail)")
    st.json(st.session_state.acta)

