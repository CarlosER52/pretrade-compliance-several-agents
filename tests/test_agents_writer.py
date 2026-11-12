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