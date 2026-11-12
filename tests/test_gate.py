"""Tests del gate humano."""

import pytest

from src.gate.compliance_gate import (
    aprobar_action,
    rechazar_action,
    validar_aprobacion,
    validar_rechazo,
)
from src.schemas import ClasificacionRiesgo


def _clasificacion(piso=False, riesgo="HIGH"):
    return ClasificacionRiesgo(
        orden_id="ORD-2026-11-00001",
        riesgo=riesgo,
        justificacion="Riesgo calculado con piso de reglas duras.",
        piso_aplicado=piso,
        riesgo_sugerido_por_agente="LOW",
        hash_inputs="abc123",
    )


def test_validar_aprobacion_rechaza_conflicto_interes():
    ctx = {
        "clasificacion": _clasificacion().model_dump(),
        "oficial": "analyst_agent",
        "firma": "firma123",
        "justificacion": "x" * 30,
        "agente_origen": "analyst_agent",
    }
    ok, msg = validar_aprobacion(ctx, {})
    assert ok is False
    assert "conflicto_interes" in msg


def test_validar_aprobacion_exige_justificacion_si_piso():
    ctx = {
        "clasificacion": _clasificacion(piso=True).model_dump(),
        "oficial": "oficial_001",
        "firma": "firma123",
        "justificacion": "corta",  # < 20 chars
        "agente_origen": "analyst_agent",
    }
    ok, msg = validar_aprobacion(ctx, {})
    assert ok is False
    assert "requiere_justificacion" in msg


def test_validar_aprobacion_ok_sin_piso():
    ctx = {
        "clasificacion": _clasificacion(piso=False).model_dump(),
        "oficial": "oficial_001",
        "firma": "firma123",
        "justificacion": "",
        "agente_origen": "analyst_agent",
    }
    ok, msg = validar_aprobacion(ctx, {})
    assert ok is True


def test_validar_rechazo_exige_justificacion():
    ctx = {
        "clasificacion": _clasificacion().model_dump(),
        "oficial": "oficial_001",
        "firma": "firma123",
        "justificacion": "corta",
    }
    ok, msg = validar_rechazo(ctx, {})
    assert ok is False
    assert "requiere_justificacion" in msg


def test_aprobar_action_produce_acta():
    ctx = {
        "clasificacion": _clasificacion(piso=True).model_dump(),
        "oficial": "oficial_001",
        "firma": "firma123",
        "justificacion": "Excepción aprobada por comité de riesgos, acta #123.",
    }
    acta = aprobar_action(ctx, {})
    assert acta["decision"] == "aprobada"
    assert acta["oficial"] == "oficial_001"
    assert acta["hash_clasificacion"] == "abc123"


def test_rechazar_action_produce_acta():
    ctx = {
        "clasificacion": _clasificacion().model_dump(),
        "oficial": "oficial_001",
        "firma": "firma123",
        "justificacion": "La orden viola la política de concentración sectorial.",
    }
    acta = rechazar_action(ctx, {})
    assert acta["decision"] == "rechazada"
    assert len(acta["justificacion"]) >= 20