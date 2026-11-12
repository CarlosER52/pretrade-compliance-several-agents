"""Genera el golden dataset de 30 casos (6 por instrumento).

Cada caso tiene:
- input: orden + contexto_cliente
- expected: reglas_fallidas, fallos_total, riesgo_minimo, piso_aplicado,
            requiere_gate, decision_esperada
- rationale: explicación legible

Uso:
    python evals/generate_golden_dataset.py
"""

import json
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "golden_dataset"


def _caso(case_id, instrumento, descripcion, orden, contexto, expected, rationale):
    return {
        "case_id": case_id,
        "instrumento": instrumento,
        "descripcion": descripcion,
        "input": {"orden": orden, "contexto_cliente": contexto},
        "expected": expected,
        "rationale": rationale,
    }


# ============================================================
# STOCKS (6 casos)
# ============================================================

STOCKS = [
    _caso(
        "stocks_001", "stocks",
        "Orden trivial: 500 TSLA, dentro de todos los límites",
        {
            "orden_id": "ORD-2026-11-10001", "instrumento": "stocks",
            "tipo": "buy", "cantidad": 500, "simbolo": "TSLA",
            "precio": 200, "tipo_orden": "limit",
            "cuenta_id": "ACC-4471", "cliente_id": "CLI-001", "sector": "tech",
        },
        {
            "capital_cuenta": 1_500_000, "posicion_actual": {"TSLA": 0},
            "exposicion_sector": {"tech": 0}, "precio_referencia": {"TSLA": 200},
            "contra_partida_cliente_id": None,
        },
        {
            "reglas_fallidas": [], "fallos_total": 0,
            "riesgo_minimo": "LOW", "piso_aplicado": False,
            "requiere_gate": False, "decision_esperada": "aprobada",
        },
        "500 * 200 = 100k, 6.67% del capital. Sin fallos. Riesgo LOW.",
    ),
    _caso(
        "stocks_002", "stocks",
        "Posición excesiva: 1000 TSLA (13.33% del capital)",
        {
            "orden_id": "ORD-2026-11-10002", "instrumento": "stocks",
            "tipo": "buy", "cantidad": 1000, "simbolo": "TSLA",
            "precio": 200, "tipo_orden": "limit",
            "cuenta_id": "ACC-4471", "cliente_id": "CLI-001", "sector": "tech",
        },
        {
            "capital_cuenta": 1_500_000, "posicion_actual": {"TSLA": 0},
            "exposicion_sector": {"tech": 0}, "precio_referencia": {"TSLA": 200},
            "contra_partida_cliente_id": None,
        },
        {
            "reglas_fallidas": ["R1_posicion"], "fallos_total": 1,
            "riesgo_minimo": "HIGH", "piso_aplicado": True,
            "requiere_gate": True, "decision_esperada": "rechazada",
        },
        "13.33% > 10%. R1 falla, piso fuerza HIGH. Gate humano debe evaluar excepción.",
    ),
    _caso(
        "stocks_003", "stocks",
        "Emisor en lista de restricción (GME)",
        {
            "orden_id": "ORD-2026-11-10003", "instrumento": "stocks",
            "tipo": "buy", "cantidad": 100, "simbolo": "GME",
            "precio": 20, "tipo_orden": "limit",
            "cuenta_id": "ACC-4471", "cliente_id": "CLI-001", "sector": "retail",
        },
        {
            "capital_cuenta": 1_500_000, "posicion_actual": {"GME": 0},
            "exposicion_sector": {"retail": 0}, "precio_referencia": {"GME": 20},
            "contra_partida_cliente_id": None,
        },
        {
            "reglas_fallidas": ["R2_lista_restringida"], "fallos_total": 1,
            "riesgo_minimo": "HIGH", "piso_aplicado": True,
            "requiere_gate": True, "decision_esperada": "rechazada",
        },
        "GME está en lista de restricción. R2 falla, piso fuerza HIGH.",
    ),
    _caso(
        "stocks_004", "stocks",
        "Cliente en watchlist con orden normal",
        {
            "orden_id": "ORD-2026-11-10004", "instrumento": "stocks",
            "tipo": "buy", "cantidad": 100, "simbolo": "AAPL",
            "precio": 180, "tipo_orden": "limit",
            "cuenta_id": "ACC-4471", "cliente_id": "CLI-001", "sector": "tech",
        },
        {
            "capital_cuenta": 1_500_000, "posicion_actual": {"AAPL": 0},
            "exposicion_sector": {"tech": 0}, "precio_referencia": {"AAPL": 180},
            "contra_partida_cliente_id": None, "cliente_en_watchlist": True,
        },
        {
            "reglas_fallidas": [], "fallos_total": 0,
            "riesgo_minimo": "MEDIUM", "piso_aplicado": True,
            "requiere_gate": True, "decision_esperada": "aprobada",
        },
        "Sin fallos de reglas, pero cliente en watchlist. El piso lo sube a MEDIUM (mínimo para watchlist).",
    ),
    _caso(
        "stocks_005", "stocks",
        "Sector prohibido (tabaco)",
        {
            "orden_id": "ORD-2026-11-10005", "instrumento": "stocks",
            "tipo": "buy", "cantidad": 100, "simbolo": "MO",
            "precio": 50, "tipo_orden": "limit",
            "cuenta_id": "ACC-4471", "cliente_id": "CLI-001", "sector": "tabaco",
        },
        {
            "capital_cuenta": 1_500_000, "posicion_actual": {"MO": 0},
            "exposicion_sector": {"tabaco": 0}, "precio_referencia": {"MO": 50},
            "contra_partida_cliente_id": None,
        },
        {
            "reglas_fallidas": ["R5_sector"], "fallos_total": 1,
            "riesgo_minimo": "HIGH", "piso_aplicado": True,
            "requiere_gate": True, "decision_esperada": "rechazada",
        },
        "Sector tabaco prohibido. R5 falla, piso fuerza HIGH.",
    ),
    _caso(
        "stocks_006", "stocks",
        "Múltiples fallos: posición + sector",
        {
            "orden_id": "ORD-2026-11-10006", "instrumento": "stocks",
            "tipo": "buy", "cantidad": 2000, "simbolo": "MO",
            "precio": 50, "tipo_orden": "limit",
            "cuenta_id": "ACC-4471", "cliente_id": "CLI-001", "sector": "tabaco",
        },
        {
            "capital_cuenta": 1_500_000, "posicion_actual": {"MO": 0},
            "exposicion_sector": {"tabaco": 0}, "precio_referencia": {"MO": 50},
            "contra_partida_cliente_id": None,
        },
        {
            "reglas_fallidas": ["R1_posicion", "R5_sector"], "fallos_total": 2,
            "riesgo_minimo": "HIGH", "piso_aplicado": True,
            "requiere_gate": True, "decision_esperada": "rechazada",
        },
        "2000*50=100k (6.67%, OK por R1), pero sector tabaco falla R5. Múltiples fallos.",
    ),
]


# ============================================================
# FOREX (6 casos)
# ============================================================

FOREX = [
    _caso(
        "forex_001", "forex", "Orden trivial EUR/USD dentro de horario",
        {
            "orden_id": "ORD-2026-11-20001", "instrumento": "forex",
            "tipo": "buy", "cantidad": 10000, "par": "EUR/USD", "tasa": 1.08,
            "cuenta_id": "ACC-4472", "cliente_id": "CLI-002",
            "jurisdiccion_cliente": "EU", "timestamp": "2026-11-10T10:00:00",
        },
        {
            "capital_cuenta": 1_000_000, "exposicion_par": {},
            "tasa_referencia": {"EUR/USD": 1.08},
            "jurisdiccion_cliente": "EU", "contraparte": "BANK_A",
        },
        {"reglas_fallidas": [], "fallos_total": 0, "riesgo_minimo": "LOW",
         "piso_aplicado": False, "requiere_gate": False,
         "decision_esperada": "aprobada"},
        "10k * 1.08 = 10.8k, 1.08% del capital. Sin fallos.",
    ),
    _caso(
        "forex_002", "forex", "Exposición excesiva en el par",
        {
            "orden_id": "ORD-2026-11-20002", "instrumento": "forex",
            "tipo": "buy", "cantidad": 200_000, "par": "EUR/USD", "tasa": 1.08,
            "cuenta_id": "ACC-4472", "cliente_id": "CLI-002",
            "jurisdiccion_cliente": "EU", "timestamp": "2026-11-10T10:00:00",
        },
        {
            "capital_cuenta": 500_000, "exposicion_par": {},
            "tasa_referencia": {"EUR/USD": 1.08},
            "jurisdiccion_cliente": "EU", "contraparte": "BANK_A",
        },
        {"reglas_fallidas": ["R1_exposicion_par"], "fallos_total": 1,
         "riesgo_minimo": "HIGH", "piso_aplicado": True,
         "requiere_gate": True, "decision_esperada": "rechazada"},
        "200k*1.08=216k, 43.2% de 500k > 20%. R1 falla.",
    ),
    _caso(
        "forex_003", "forex", "Fuera de horario de liquidación",
        {
            "orden_id": "ORD-2026-11-20003", "instrumento": "forex",
            "tipo": "buy", "cantidad": 10000, "par": "EUR/USD", "tasa": 1.08,
            "cuenta_id": "ACC-4472", "cliente_id": "CLI-002",
            "jurisdiccion_cliente": "EU", "timestamp": "2026-11-10T03:00:00",
        },
        {
            "capital_cuenta": 1_000_000, "exposicion_par": {},
            "tasa_referencia": {"EUR/USD": 1.08},
            "jurisdiccion_cliente": "EU", "contraparte": "BANK_A",
        },
        {"reglas_fallidas": ["R2_horario_liquidacion"], "fallos_total": 1,
         "riesgo_minimo": "HIGH", "piso_aplicado": True,
         "requiere_gate": True, "decision_esperada": "rechazada"},
        "03:00 UTC fuera de la ventana 07:00-16:00. R2 falla.",
    ),
    _caso(
        "forex_004", "forex", "Jurisdicción restringida",
        {
            "orden_id": "ORD-2026-11-20004", "instrumento": "forex",
            "tipo": "buy", "cantidad": 10000, "par": "EUR/USD", "tasa": 1.08,
            "cuenta_id": "ACC-4472", "cliente_id": "CLI-002",
            "jurisdiccion_cliente": "IR", "timestamp": "2026-11-10T10:00:00",
        },
        {
            "capital_cuenta": 1_000_000, "exposicion_par": {},
            "tasa_referencia": {"EUR/USD": 1.08},
            "jurisdiccion_cliente": "IR", "contraparte": "BANK_A",
        },
        {"reglas_fallidas": ["R3_jurisdiccion"], "fallos_total": 1,
         "riesgo_minimo": "HIGH", "piso_aplicado": True,
         "requiere_gate": True, "decision_esperada": "rechazada"},
        "IR está en jurisdicciones restringidas para EUR/USD. R3 falla.",
    ),
    _caso(
        "forex_005", "forex", "Contraparte no aprobada",
        {
            "orden_id": "ORD-2026-11-20005", "instrumento": "forex",
            "tipo": "buy", "cantidad": 10000, "par": "EUR/USD", "tasa": 1.08,
            "cuenta_id": "ACC-4472", "cliente_id": "CLI-002",
            "jurisdiccion_cliente": "EU", "timestamp": "2026-11-10T10:00:00",
        },
        {
            "capital_cuenta": 1_000_000, "exposicion_par": {},
            "tasa_referencia": {"EUR/USD": 1.08},
            "jurisdiccion_cliente": "EU", "contraparte": "BANK_Z",
        },
        {"reglas_fallidas": ["R5_contraparte"], "fallos_total": 1,
         "riesgo_minimo": "HIGH", "piso_aplicado": True,
         "requiere_gate": True, "decision_esperada": "rechazada"},
        "BANK_Z no está en contrapartes aprobadas. R5 falla.",
    ),
    _caso(
        "forex_006", "forex", "Múltiples fallos: exposición + horario",
        {
            "orden_id": "ORD-2026-11-20006", "instrumento": "forex",
            "tipo": "buy", "cantidad": 200_000, "par": "EUR/USD", "tasa": 1.08,
            "cuenta_id": "ACC-4472", "cliente_id": "CLI-002",
            "jurisdiccion_cliente": "EU", "timestamp": "2026-11-10T03:00:00",
        },
        {
            "capital_cuenta": 500_000, "exposicion_par": {},
            "tasa_referencia": {"EUR/USD": 1.08},
            "jurisdiccion_cliente": "EU", "contraparte": "BANK_A",
        },
        {"reglas_fallidas": ["R1_exposicion_par", "R2_horario_liquidacion"],
         "fallos_total": 2, "riesgo_minimo": "HIGH", "piso_aplicado": True,
         "requiere_gate": True, "decision_esperada": "rechazada"},
        "Exposición 43.2% Y fuera de horario. Dos fallos.",
    ),
]


# ============================================================
# CRYPTO (6 casos)
# ============================================================

CRYPTO = [
    _caso(
        "crypto_001", "crypto", "Orden trivial BTC en exchange permitido",
        {
            "orden_id": "ORD-2026-11-30001", "instrumento": "crypto",
            "tipo": "buy", "cantidad": 0.5, "token": "BTC",
            "exchange": "BINANCE", "precio": 60000,
            "cuenta_id": "ACC-4473", "cliente_id": "CLI-003",
            "jurisdiccion_cliente": "EU",
        },
        {
            "capital_cuenta": 1_000_000, "exposicion_exchange": {},
            "precio_referencia": {"BTC": 60000}, "jurisdiccion_cliente": "EU",
        },
        {"reglas_fallidas": [], "fallos_total": 0, "riesgo_minimo": "LOW",
         "piso_aplicado": False, "requiere_gate": False,
         "decision_esperada": "aprobada"},
        "0.5*60k=30k, 3% del capital. Sin fallos.",
    ),
    _caso(
        "crypto_002", "crypto", "Token no permitido (SHIB)",
        {
            "orden_id": "ORD-2026-11-30002", "instrumento": "crypto",
            "tipo": "buy", "cantidad": 1_000_000, "token": "SHIB",
            "exchange": "BINANCE", "precio": 0.00001,
            "cuenta_id": "ACC-4473", "cliente_id": "CLI-003",
            "jurisdiccion_cliente": "EU",
        },
        {
            "capital_cuenta": 1_000_000, "exposicion_exchange": {},
            "precio_referencia": {"SHIB": 0.00001}, "jurisdiccion_cliente": "EU",
        },
        {"reglas_fallidas": ["R1_activo_permitido"], "fallos_total": 1,
         "riesgo_minimo": "HIGH", "piso_aplicado": True,
         "requiere_gate": True, "decision_esperada": "rechazada"},
        "SHIB no está en TOKENS_PERMITIDOS. R1 falla.",
    ),
    _caso(
        "crypto_003", "crypto", "Token en watchlist regulatoria (XRP)",
        {
            "orden_id": "ORD-2026-11-30003", "instrumento": "crypto",
            "tipo": "buy", "cantidad": 1000, "token": "XRP",
            "exchange": "BINANCE", "precio": 0.5,
            "cuenta_id": "ACC-4473", "cliente_id": "CLI-003",
            "jurisdiccion_cliente": "EU",
        },
        {
            "capital_cuenta": 1_000_000, "exposicion_exchange": {},
            "precio_referencia": {"XRP": 0.5}, "jurisdiccion_cliente": "EU",
        },
        {"reglas_fallidas": ["R4_watchlist_regulatoria"], "fallos_total": 1,
         "riesgo_minimo": "HIGH", "piso_aplicado": True,
         "requiere_gate": True, "decision_esperada": "rechazada"},
        "XRP está en watchlist regulatoria. R4 falla.",
    ),
    _caso(
        "crypto_004", "crypto", "Jurisdicción no permitida para SOL",
        {
            "orden_id": "ORD-2026-11-30004", "instrumento": "crypto",
            "tipo": "buy", "cantidad": 10, "token": "SOL",
            "exchange": "BINANCE", "precio": 150,
            "cuenta_id": "ACC-4473", "cliente_id": "CLI-003",
            "jurisdiccion_cliente": "CN",
        },
        {
            "capital_cuenta": 1_000_000, "exposicion_exchange": {},
            "precio_referencia": {"SOL": 150}, "jurisdiccion_cliente": "CN",
        },
        {"reglas_fallidas": ["R3_jurisdiccion"], "fallos_total": 1,
         "riesgo_minimo": "HIGH", "piso_aplicado": True,
         "requiere_gate": True, "decision_esperada": "rechazada"},
        "CN no está en jurisdicciones permitidas para SOL. R3 falla.",
    ),
    _caso(
        "crypto_005", "crypto", "Exposición excesiva en exchange",
        {
            "orden_id": "ORD-2026-11-30005", "instrumento": "crypto",
            "tipo": "buy", "cantidad": 100, "token": "ETH",
            "exchange": "BINANCE", "precio": 3000,
            "cuenta_id": "ACC-4473", "cliente_id": "CLI-003",
            "jurisdiccion_cliente": "EU",
        },
        {
            "capital_cuenta": 500_000, "exposicion_exchange": {"BINANCE": 0},
            "precio_referencia": {"ETH": 3000}, "jurisdiccion_cliente": "EU",
        },
        {"reglas_fallidas": ["R2_limite_exchange"], "fallos_total": 1,
         "riesgo_minimo": "HIGH", "piso_aplicado": True,
         "requiere_gate": True, "decision_esperada": "rechazada"},
        "100*3000=300k, 60% de 500k > 30%. R2 falla.",
    ),
    _caso(
        "crypto_006", "crypto", "Múltiples fallos: token + jurisdicción",
        {
            "orden_id": "ORD-2026-11-30006", "instrumento": "crypto",
            "tipo": "buy", "cantidad": 1000, "token": "SHIB",
            "exchange": "BINANCE", "precio": 0.00001,
            "cuenta_id": "ACC-4473", "cliente_id": "CLI-003",
            "jurisdiccion_cliente": "CN",
        },
        {
            "capital_cuenta": 1_000_000, "exposicion_exchange": {},
            "precio_referencia": {"SHIB": 0.00001}, "jurisdiccion_cliente": "CN",
        },
        {"reglas_fallidas": ["R1_activo_permitido", "R3_jurisdiccion"],
         "fallos_total": 2, "riesgo_minimo": "HIGH", "piso_aplicado": True,
         "requiere_gate": True, "decision_esperada": "rechazada"},
        "SHIB no permitido Y CN no permitido. Dos fallos.",
    ),
]


# ============================================================
# FUTURES (6 casos)
# ============================================================

FUTURES = [
    _caso(
        "futures_001", "futures", "Orden trivial ESZ6 dentro de márgenes",
        {
            "orden_id": "ORD-2026-11-40001", "instrumento": "futures",
            "tipo": "buy", "cantidad": 10, "contrato": "ESZ6",
            "vencimiento": "2026-12-18", "margen_disponible": 500_000,
            "precio": 4500, "cuenta_id": "ACC-4474", "cliente_id": "CLI-004",
            "timestamp": "2026-11-10T15:00:00",
        },
        {"posicion_vencimiento": {}, "es_roll": False},
        {"reglas_fallidas": [], "fallos_total": 0, "riesgo_minimo": "LOW",
         "piso_aplicado": False, "requiere_gate": False,
         "decision_esperada": "aprobada"},
        "10*15k=150k margen requerido, 500k disponible. Sin fallos.",
    ),
    _caso(
        "futures_002", "futures", "Margen insuficiente",
        {
            "orden_id": "ORD-2026-11-40002", "instrumento": "futures",
            "tipo": "buy", "cantidad": 10, "contrato": "ESZ6",
            "vencimiento": "2026-12-18", "margen_disponible": 100_000,
            "precio": 4500, "cuenta_id": "ACC-4474", "cliente_id": "CLI-004",
            "timestamp": "2026-11-10T15:00:00",
        },
        {"posicion_vencimiento": {}, "es_roll": False},
        {"reglas_fallidas": ["R1_margen"], "fallos_total": 1,
         "riesgo_minimo": "HIGH", "piso_aplicado": True,
         "requiere_gate": True, "decision_esperada": "rechazada"},
        "10*15k=150k > 100k disponible. R1 falla.",
    ),
    _caso(
        "futures_003", "futures", "Límite de contratos excedido",
        {
            "orden_id": "ORD-2026-11-40003", "instrumento": "futures",
            "tipo": "buy", "cantidad": 60, "contrato": "ESZ6",
            "vencimiento": "2026-12-18", "margen_disponible": 2_000_000,
            "precio": 4500, "cuenta_id": "ACC-4474", "cliente_id": "CLI-004",
            "timestamp": "2026-11-10T15:00:00",
        },
        {"posicion_vencimiento": {}, "es_roll": False},
        {"reglas_fallidas": ["R4_limite_contratos"], "fallos_total": 1,
         "riesgo_minimo": "HIGH", "piso_aplicado": True,
         "requiere_gate": True, "decision_esperada": "rechazada"},
        "60 > 50 contratos máximos. R4 falla.",
    ),
    _caso(
        "futures_004", "futures", "Fuera de sesión de mercado",
        {
            "orden_id": "ORD-2026-11-40004", "instrumento": "futures",
            "tipo": "buy", "cantidad": 10, "contrato": "ESZ6",
            "vencimiento": "2026-12-18", "margen_disponible": 500_000,
            "precio": 4500, "cuenta_id": "ACC-4474", "cliente_id": "CLI-004",
            "timestamp": "2026-11-10T03:00:00",
        },
        {"posicion_vencimiento": {}, "es_roll": False},
        {"reglas_fallidas": ["R5_sesion"], "fallos_total": 1,
         "riesgo_minimo": "HIGH", "piso_aplicado": True,
         "requiere_gate": True, "decision_esperada": "rechazada"},
        "03:00 UTC fuera de sesión 13:30-20:00. R5 falla.",
    ),
    _caso(
        "futures_005", "futures", "Límite de vencimiento excedido",
        {
            "orden_id": "ORD-2026-11-40005", "instrumento": "futures",
            "tipo": "buy", "cantidad": 10, "contrato": "ESZ6",
            "vencimiento": "2026-12-18", "margen_disponible": 500_000,
            "precio": 4500, "cuenta_id": "ACC-4474", "cliente_id": "CLI-004",
            "timestamp": "2026-11-10T15:00:00",
        },
        {"posicion_vencimiento": {"2026-12-18": 95}, "es_roll": False},
        {"reglas_fallidas": ["R2_limite_vencimiento"], "fallos_total": 1,
         "riesgo_minimo": "HIGH", "piso_aplicado": True,
         "requiere_gate": True, "decision_esperada": "rechazada"},
        "95+10=105 > 100 límite por vencimiento. R2 falla.",
    ),
    _caso(
        "futures_006", "futures", "Múltiples fallos: margen + contratos",
        {
            "orden_id": "ORD-2026-11-40006", "instrumento": "futures",
            "tipo": "buy", "cantidad": 60, "contrato": "ESZ6",
            "vencimiento": "2026-12-18", "margen_disponible": 100_000,
            "precio": 4500, "cuenta_id": "ACC-4474", "cliente_id": "CLI-004",
            "timestamp": "2026-11-10T15:00:00",
        },
        {"posicion_vencimiento": {}, "es_roll": False},
        {"reglas_fallidas": ["R1_margen", "R4_limite_contratos"],
         "fallos_total": 2, "riesgo_minimo": "HIGH", "piso_aplicado": True,
         "requiere_gate": True, "decision_esperada": "rechazada"},
        "Margen insuficiente Y 60 contratos > 50. Dos fallos.",
    ),
]


# ============================================================
# OPTIONS (6 casos)
# ============================================================

OPTIONS = [
    _caso(
        "options_001", "options", "Orden trivial: covered call nivel 2",
        {
            "orden_id": "ORD-2026-11-50001", "instrumento": "options",
            "tipo": "buy", "cantidad": 10, "subyacente": "AAPL",
            "tipo_opcion": "call", "strike": 180, "vencimiento": "2027-01-15",
            "nivel_aprobacion_cliente": 2, "estrategia": "covered",
            "cuenta_id": "ACC-4475", "cliente_id": "CLI-005",
        },
        {"delta_total": 100.0, "delta_orden": 50.0},
        {"reglas_fallidas": [], "fallos_total": 0, "riesgo_minimo": "LOW",
         "piso_aplicado": False, "requiere_gate": False,
         "decision_esperada": "aprobada"},
        "Covered call, nivel 2 >= 1 requerido. Delta 150 < 500. Sin fallos.",
    ),
    _caso(
        "options_002", "options", "Nivel insuficiente para naked",
        {
            "orden_id": "ORD-2026-11-50002", "instrumento": "options",
            "tipo": "buy", "cantidad": 10, "subyacente": "AAPL",
            "tipo_opcion": "call", "strike": 180, "vencimiento": "2027-01-15",
            "nivel_aprobacion_cliente": 2, "estrategia": "naked",
            "cuenta_id": "ACC-4475", "cliente_id": "CLI-005",
        },
        {"delta_total": 100.0, "delta_orden": 50.0},
        {"reglas_fallidas": ["R1_nivel_aprobacion"], "fallos_total": 1,
         "riesgo_minimo": "HIGH", "piso_aplicado": True,
         "requiere_gate": True, "decision_esperada": "rechazada"},
        "Naked requiere nivel 4, cliente tiene 2. R1 falla.",
    ),
    _caso(
        "options_003", "options", "Naked put con nivel 3 (requiere 4+)",
        {
            "orden_id": "ORD-2026-11-50003", "instrumento": "options",
            "tipo": "sell", "cantidad": 10, "subyacente": "AAPL",
            "tipo_opcion": "put", "strike": 180, "vencimiento": "2027-01-15",
            "nivel_aprobacion_cliente": 3, "estrategia": "naked",
            "cuenta_id": "ACC-4475", "cliente_id": "CLI-005",
        },
        {"delta_total": 100.0, "delta_orden": -50.0},
        {"reglas_fallidas": ["R4_naked_put"], "fallos_total": 1,
         "riesgo_minimo": "HIGH", "piso_aplicado": True,
         "requiere_gate": True, "decision_esperada": "rechazada"},
        "Naked put requiere nivel 4+, cliente tiene 3. R4 falla.",
    ),
    _caso(
        "options_004", "options", "Delta excedido",
        {
            "orden_id": "ORD-2026-11-50004", "instrumento": "options",
            "tipo": "buy", "cantidad": 10, "subyacente": "AAPL",
            "tipo_opcion": "call", "strike": 180, "vencimiento": "2027-01-15",
            "nivel_aprobacion_cliente": 4, "estrategia": "spread",
            "cuenta_id": "ACC-4475", "cliente_id": "CLI-005",
        },
        {"delta_total": 400.0, "delta_orden": 150.0},
        {"reglas_fallidas": ["R3_limite_griegas"], "fallos_total": 1,
         "riesgo_minimo": "HIGH", "piso_aplicado": True,
         "requiere_gate": True, "decision_esperada": "rechazada"},
        "400+150=550 > 500 límite de delta. R3 falla.",
    ),
    _caso(
        "options_005", "options", "Vencimiento muy corto (3 días)",
        {
            "orden_id": "ORD-2026-11-50005", "instrumento": "options",
            "tipo": "buy", "cantidad": 10, "subyacente": "AAPL",
            "tipo_opcion": "call", "strike": 180, "vencimiento": "2026-11-13",
            "nivel_aprobacion_cliente": 4, "estrategia": "spread",
            "cuenta_id": "ACC-4475", "cliente_id": "CLI-005",
            "timestamp": "2026-11-10T12:00:00",
        },
        {"delta_total": 100.0, "delta_orden": 50.0},
        {"reglas_fallidas": ["R5_vencimiento"], "fallos_total": 1,
         "riesgo_minimo": "HIGH", "piso_aplicado": True,
         "requiere_gate": True, "decision_esperada": "rechazada"},
        "Vencimiento en 3 días < 7 mínimo. R5 falla.",
    ),
    _caso(
        "options_006", "options", "Múltiples fallos: nivel + griegas",
        {
            "orden_id": "ORD-2026-11-50006", "instrumento": "options",
            "tipo": "buy", "cantidad": 10, "subyacente": "AAPL",
            "tipo_opcion": "call", "strike": 180, "vencimiento": "2027-01-15",
            "nivel_aprobacion_cliente": 1, "estrategia": "naked",
            "cuenta_id": "ACC-4475", "cliente_id": "CLI-005",
        },
        {"delta_total": 400.0, "delta_orden": 150.0},
        {"reglas_fallidas": ["R1_nivel_aprobacion", "R2_estrategia_permitida",
                             "R3_limite_griegas"],
         "fallos_total": 3, "riesgo_minimo": "HIGH", "piso_aplicado": True,
         "requiere_gate": True, "decision_esperada": "rechazada"},
        "Nivel 1 para naked (requiere 4+), estrategia no permitida, delta excedido. Tres fallos.",
    ),
]


TODOS = STOCKS + FOREX + CRYPTO + FUTURES + OPTIONS


def main():
    assert len(TODOS) == 30, f"Esperado 30 casos, hay {len(TODOS)}"
    for caso in TODOS:
        inst = caso["instrumento"]
        out_dir = OUTPUT_DIR / inst
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"{caso['case_id']}.json"
        out_file.write_text(
            json.dumps(caso, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"  [write] {out_file.relative_to(OUTPUT_DIR.parent)}")
    print(f"\nGenerados {len(TODOS)} casos en {OUTPUT_DIR}")


if __name__ == "__main__":
    main()