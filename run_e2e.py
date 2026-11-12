"""Flujo end-to-end: orden -> archivada."""

from src.agents.analyst import analyst_agent_action
from src.agents.writer import writer_agent_action
from src.petri.transitions import (
    calcular_hash,
    clasificar_con_piso_action,
    ejecutar_reglas_action,
    validar_schema_action,
)
from src.gate.compliance_gate import (
    aprobar_action,
    enqueue_action,
    rechazar_action,
    validar_aprobacion,
    validar_rechazo,
)
from src.archive.audit_trail import archivar_action, validar_archivo


def run(orden: dict, contexto_cliente: dict, decision: str = "aprobar"):
    print("=" * 60)
    print(f"ORDEN {orden['orden_id']}")
    print("=" * 60)

    # 1. Validar schema
    schema = validar_schema_action({"orden": orden}, {})
    if not schema["ok"]:
        print(f"[ERROR] schema: {schema['error']}")
        return
    print("[1/6] Schema OK")

    # 2. Reglas duras
    v = ejecutar_reglas_action(
        {"orden": orden, "contexto_cliente": contexto_cliente}, {}
    )
    print(f"[2/6] Reglas: {v['fallos_total']} fallos")
    for r in v["reglas"]:
        if r["resultado"] == "fail":
            print(f"       - {r['regla_id']}: {r['detalle']}")

    # 3. Agente analista (LLM)
    analisis = analyst_agent_action(
        {"orden": orden, "validacion": v, "contexto_cliente": contexto_cliente},
        {},
    )
    print(f"[3/6] Análisis: watchlist={analisis['cliente_en_watchlist']}, "
          f"patron={analisis['patron_inusual']}, conf={analisis['confianza']}")

    # 4. Clasificación con piso
    c = clasificar_con_piso_action(
        {"validacion": v, "analisis": analisis,
         "riesgo_sugerido_por_agente": "LOW"},
        {},
    )
    print(f"[4/6] Riesgo: {c['riesgo']} (piso={c['piso_aplicado']})")

    # 4.5. Redactor de memo (LLM)
    memo = writer_agent_action({
        "orden": orden,
        "validacion": v,
        "analisis": analisis,
        "clasificacion": c,
    }, {})
    print(f"[4.5/6] Memo redactado ({len(memo['memo'])} chars)")

    # 5. Enviar a gate
    enq = enqueue_action({"clasificacion": c}, {})
    print(f"[5/6] Encolada en gate: {enq['orden_id']}")

    # 6. Gate humano
    gate_ctx = {
        "clasificacion": c,
        "oficial": "oficial_001",
        "firma": "firma_digital_abc123",
        "justificacion": (
            "Excepción aprobada por comité de riesgos, acta #123."
            if decision == "aprobar" else
            "La orden viola la política de posición y no hay excepción."
        ),
        "agente_origen": "analyst_agent",
    }

    if decision == "aprobar":
        ok, msg = validar_aprobacion(gate_ctx, {})
        if not ok:
            print(f"[GATE] rechazado por guarda: {msg}")
            return
        acta = aprobar_action(gate_ctx, {})
    else:
        ok, msg = validar_rechazo(gate_ctx, {})
        if not ok:
            print(f"[GATE] rechazado por guarda: {msg}")
            return
        acta = rechazar_action(gate_ctx, {})

    print(f"[6/6] Acta: {acta['decision']} por {acta['oficial']}")

    # 7. Archivar
    arch_ctx = {
        "acta": acta,
        "artefactos": {
            "orden": orden,
            "validacion_reglas": v,
            "analisis_contexto": analisis,
            "clasificacion_riesgo": c,
            "memo": memo,
        },
    }
    ok, msg = validar_archivo(arch_ctx, {})
    if not ok:
        print(f"[ARCHIVO] {msg}")
        return
    audit = archivar_action(arch_ctx, {})
    print(f"[ARCHIVO] idempotency_key: {audit['idempotency_key'][:16]}...")
    print("=" * 60)


if __name__ == "__main__":
    orden = {
        "orden_id": "ORD-2026-11-00001",
        "instrumento": "stocks",
        "tipo": "buy",
        "cantidad": 1000,
        "simbolo": "TSLA",
        "precio": 200,
        "tipo_orden": "limit",
        "cuenta_id": "ACC-4471",
        "cliente_id": "CLI-001",
        "sector": "tech",
    }
    contexto = {
        "capital_cuenta": 1_500_000,
        "posicion_actual": {"TSLA": 0},
        "exposicion_sector": {"tech": 0},
        "precio_referencia": {"TSLA": 200},
        "contra_partida_cliente_id": None,
    }
    run(orden, contexto, decision="aprobar")