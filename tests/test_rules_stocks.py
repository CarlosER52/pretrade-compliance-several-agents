"""Tests de las 5 reglas de stocks."""

import pytest

from src.rules.stocks import REGLAS_STOCKS
from src.rules.stocks.r1_posicion import R1Posicion
from src.rules.stocks.r2_lista import R2ListaRestringida
from src.rules.stocks.r3_concentracion import R3Concentracion
from src.rules.stocks.r4_wash_trading import R4WashTrading
from src.rules.stocks.r5_sector import R5Sector


# Orden base para tests
ORDEN_BASE = {
    "orden_id": "ORD-2026-11-00001",
    "instrumento": "stocks",
    "tipo": "buy",
    "cantidad": 500,
    "simbolo": "TSLA",
    "precio": None,
    "tipo_orden": "market",
    "cuenta_id": "ACC-4471",
    "cliente_id": "CLI-001",
    "sector": "tech",
}

CONTEXTO_BASE = {
    "capital_cuenta": 1_500_000,
    "posicion_actual": {"TSLA": 0},
    "exposicion_sector": {"tech": 0},
    "precio_referencia": {"TSLA": 200},
    "contra_partida_cliente_id": None,
}


def test_r1_posicion_falla_si_supera_10pct():
    # 500 * 200 = 100,000; 100,000 / 1,500,000 = 6.67% -> no falla
    orden = {**ORDEN_BASE, "cantidad": 500}
    r = R1Posicion().evaluar(orden, CONTEXTO_BASE)
    assert r.resultado == "pass"

    # 1000 * 200 = 200,000; 200,000 / 1,500,000 = 13.3% -> falla
    orden_mal = {**ORDEN_BASE, "cantidad": 1000}
    r_mal = R1Posicion().evaluar(orden_mal, CONTEXTO_BASE)
    assert r_mal.resultado == "fail"
    assert "supera límite" in r_mal.detalle


def test_r2_lista_falla_si_simbolo_restringido():
    orden = {**ORDEN_BASE, "simbolo": "GME"}
    r = R2ListaRestringida().evaluar(orden, CONTEXTO_BASE)
    assert r.resultado == "fail"
    assert "lista de restricción" in r.detalle

    orden_ok = {**ORDEN_BASE, "simbolo": "TSLA"}
    r_ok = R2ListaRestringida().evaluar(orden_ok, CONTEXTO_BASE)
    assert r_ok.resultado == "pass"


def test_r3_concentracion_falla_si_sector_supera_25pct():
    # tech = 0, añadir 500*200 = 100,000 -> 6.67% -> pass
    r = R3Concentracion().evaluar(ORDEN_BASE, CONTEXTO_BASE)
    assert r.resultado == "pass"

    # Añadir 2000*200 = 400,000 -> 26.67% -> fail
    orden_mal = {**ORDEN_BASE, "cantidad": 2000}
    r_mal = R3Concentracion().evaluar(orden_mal, CONTEXTO_BASE)
    assert r_mal.resultado == "fail"


def test_r4_wash_trading_falla_si_cliente_contra_si_mismo():
    contexto = {**CONTEXTO_BASE, "contra_partida_cliente_id": "CLI-001"}
    r = R4WashTrading().evaluar(ORDEN_BASE, contexto)
    assert r.resultado == "fail"
    assert "contra sí mismo" in r.detalle

    contexto_ok = {**CONTEXTO_BASE, "contra_partida_cliente_id": "CLI-999"}
    r_ok = R4WashTrading().evaluar(ORDEN_BASE, contexto_ok)
    assert r_ok.resultado == "pass"


def test_r5_sector_falla_si_sector_prohibido():
    orden = {**ORDEN_BASE, "sector": "tabaco"}
    r = R5Sector().evaluar(orden, CONTEXTO_BASE)
    assert r.resultado == "fail"
    assert "prohibido" in r.detalle

    orden_ok = {**ORDEN_BASE, "sector": "tech"}
    r_ok = R5Sector().evaluar(orden_ok, CONTEXTO_BASE)
    assert r_ok.resultado == "pass"


def test_reglas_stocks_tiene_5_reglas():
    assert len(REGLAS_STOCKS) == 5
    ids = {r.regla_id for r in REGLAS_STOCKS}
    assert ids == {
        "R1_posicion", "R2_lista_restringida", "R3_concentracion",
        "R4_wash_trading", "R5_sector",
    }