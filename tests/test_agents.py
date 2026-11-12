"""Tests del agente analista con LLM mockeado."""

from unittest.mock import MagicMock, patch

import pytest

from src.agents.analyst import AnalystAgent
from src.schemas import AnalisisContexto, ReglaResultado, ValidacionReglas


@pytest.fixture
def validacion_stub():
    return ValidacionReglas(
        orden_id="ORD-2026-11-00001",
        instrumento="stocks",
        reglas=[
            ReglaResultado(
                regla_id="R1_posicion",
                resultado="fail",
                detalle="Posición resultante 13.33% supera límite 10.00%",
                valor_observado=0.1333,
                limite=0.10,
            )
        ],
        fallos_total=1,
        hash_inputs="abc123",
    )


@pytest.fixture
def orden_stub():
    return {
        "orden_id": "ORD-2026-11-00001",
        "instrumento": "stocks",
        "tipo": "buy",
        "cantidad": 1000,
        "simbolo": "TSLA",
        "precio": 200,
        "cuenta_id": "ACC-4471",
        "cliente_id": "CLI-001",
        "sector": "tech",
    }


def test_analyst_rellena_campos_de_trazabilidad(orden_stub, validacion_stub):
    """El agente debe rellenar orden_id y hash_inputs aunque el LLM no los dé."""
    agente = AnalystAgent(llm_client=MagicMock())

    # Mock: el LLM devuelve un AnalisisContexto con campos vacíos de trazabilidad
    analisis_llm = AnalisisContexto(
        orden_id="",  # vacío a propósito
        cliente_en_watchlist=False,
        patron_inusual=True,
        conflicto_politica=True,
        justificacion="Orden 3x mayor que el promedio del cliente.",
        confianza=0.85,
        hash_inputs="",  # vacío a propósito
    )
    agente.llm.parse_structured.return_value = analisis_llm

    resultado = agente.analizar(orden_stub, validacion_stub, {"capital_cuenta": 1_500_000})

    # Trazabilidad rellenada por el agente, no por el LLM
    assert resultado.orden_id == "ORD-2026-11-00001"
    assert resultado.hash_inputs != ""
    # Campos del LLM preservados
    assert resultado.patron_inusual is True
    assert resultado.confianza == 0.85


def test_analyst_pasa_prompt_con_datos(orden_stub, validacion_stub):
    """El user_prompt debe incluir la orden y el resultado de reglas."""
    agente = AnalystAgent(llm_client=MagicMock())
    agente.llm.parse_structured.return_value = AnalisisContexto(
        orden_id="", cliente_en_watchlist=False, patron_inusual=False,
        conflicto_politica=False, justificacion="x" * 20, confianza=0.5,
        hash_inputs="",
    )

    agente.analizar(orden_stub, validacion_stub, {})

    # Verificar que el prompt contiene la orden y el fallo de R1
    call_args = agente.llm.parse_structured.call_args
    user_prompt = call_args.kwargs["user_prompt"]
    assert "ORD-2026-11-00001" in user_prompt
    assert "R1_posicion" in user_prompt
    assert "13.33%" in user_prompt

def test_writer_redacta_memo(orden_stub, validacion_stub):
    """El redactor debe devolver un string markdown no vacío."""
    from unittest.mock import MagicMock
    from src.agents.writer import WriterAgent
    from src.schemas import AnalisisContexto, ClasificacionRiesgo

    agente = WriterAgent(llm_client=MagicMock())

    # Mock: el LLM devuelve un memo markdown
    agente.llm.client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="# Memo de Compliance\n\n## 1. Resumen\n..."))]
    )

    analisis = AnalisisContexto(
        orden_id="ORD-2026-11-00001", cliente_en_watchlist=False,
        patron_inusual=True, conflicto_politica=True,
        justificacion="Orden 3x mayor que el promedio.", confianza=0.9,
        hash_inputs="abc",
    )
    clasificacion = ClasificacionRiesgo(
        orden_id="ORD-2026-11-00001", riesgo="HIGH",
        justificacion="Piso aplicado por R1.", piso_aplicado=True,
        riesgo_sugerido_por_agente="LOW", hash_inputs="abc",
    )

    memo = agente.redactar_memo(orden_stub, validacion_stub, analisis, clasificacion)

    assert isinstance(memo, str)
    assert len(memo) > 0
    assert "Memo" in memo


def test_writer_wrapper_devuelve_dict(orden_stub, validacion_stub):
    """El wrapper debe devolver dict con orden_id y memo."""
    from unittest.mock import MagicMock, patch
    from src.agents.writer import writer_agent_action

    with patch("src.agents.writer._get_writer") as mock_get:
        mock_writer = MagicMock()
        mock_writer.redactar_memo.return_value = "# Memo\n\nContenido."
        mock_get.return_value = mock_writer

        resultado = writer_agent_action(
            {
                "orden": orden_stub,
                "validacion": validacion_stub.model_dump(),
                "analisis": {
                    "orden_id": "ORD-2026-11-00001",
                    "cliente_en_watchlist": False,
                    "patron_inusual": True,
                    "conflicto_politica": True,
                    "justificacion": "x" * 20,
                    "confianza": 0.9,
                    "hash_inputs": "abc",
                },
                "clasificacion": {
                    "orden_id": "ORD-2026-11-00001",
                    "riesgo": "HIGH",
                    "justificacion": "x" * 20,
                    "piso_aplicado": True,
                    "hash_inputs": "abc",
                },
            },
            {},
        )

    assert resultado["orden_id"] == "ORD-2026-11-00001"
    assert "Memo" in resultado["memo"]