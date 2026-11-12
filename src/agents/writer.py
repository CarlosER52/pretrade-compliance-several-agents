"""Agente redactor de memo de compliance.

Produce un memo en markdown a partir de la orden, la validación de reglas,
el análisis de contexto y la clasificación de riesgo. Es una función
determinista con un LLM detrás: una sola llamada, output en texto libre,
sin agencia autónoma.
"""

import json
from pathlib import Path

from src.agents.llm_client import LLMClient
from src.schemas import (
    AnalisisContexto,
    ClasificacionRiesgo,
    ValidacionReglas,
)

# Cargar el prompt desde archivo (separado del código para auditoría)
_PROMPT_PATH = Path(__file__).parent / "prompts" / "writer.md"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text(encoding="utf-8")


class WriterAgent:
    """Agente redactor de memo de compliance con LLM."""

    def __init__(self, llm_client: LLMClient | None = None):
        self.llm = llm_client or LLMClient()

    def redactar_memo(
        self,
        orden: dict,
        validacion: ValidacionReglas,
        analisis: AnalisisContexto,
        clasificacion: ClasificacionRiesgo,
    ) -> str:
        """Redacta el memo de compliance y lo devuelve como markdown.

        Una sola llamada al LLM, temperatura baja para consistencia.
        """
        user_prompt = self._build_user_prompt(
            orden, validacion, analisis, clasificacion
        )

        # El redactor usa texto libre, no JSON estructurado.
        # Por eso llama directamente al cliente sin parse_structured.
        response = self.llm.client.chat.completions.create(
            model=self.llm.model,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content

    def _build_user_prompt(
        self,
        orden: dict,
        validacion: ValidacionReglas,
        analisis: AnalisisContexto,
        clasificacion: ClasificacionRiesgo,
    ) -> str:
        """Construye el prompt con los datos de la orden y los artefactos.

        Usa lista de strings + '\\n'.join para evitar problemas con backticks.
        """
        orden_json = json.dumps(orden, indent=2, ensure_ascii=False, default=str)
        validacion_json = json.dumps(
            validacion.model_dump(), indent=2, ensure_ascii=False, default=str
        )
        analisis_json = json.dumps(
            analisis.model_dump(), indent=2, ensure_ascii=False, default=str
        )
        clasificacion_json = json.dumps(
            clasificacion.model_dump(), indent=2, ensure_ascii=False, default=str
        )

        partes = [
            f"Redacta el memo de compliance para la orden "
            f"{orden.get('orden_id', 'N/A')}.",
            "",
            "--- ORDEN PROPUESTA ---",
            orden_json,
            "",
            "--- RESULTADO DE REGLAS DURAS ---",
            validacion_json,
            "",
            "--- ANÁLISIS DE CONTEXTO ---",
            analisis_json,
            "",
            "--- CLASIFICACIÓN DE RIESGO ---",
            clasificacion_json,
            "",
            "Produce el memo en markdown según la estructura solicitada.",
        ]
        return "\n".join(partes)


# ------------------------------------------------------------
# Wrapper para el motor de Petri
# ------------------------------------------------------------

_writer_agent: WriterAgent | None = None


def _get_writer() -> WriterAgent:
    global _writer_agent
    if _writer_agent is None:
        _writer_agent = WriterAgent()
    return _writer_agent


def writer_agent_action(context: dict, places: dict) -> dict:
    """Acción de la transición `t_redactar_memo`.

    Requiere en `context`:
        - `orden`: dict.
        - `validacion`: ValidacionReglas (o dict).
        - `analisis`: AnalisisContexto (o dict).
        - `clasificacion`: ClasificacionRiesgo (o dict).

    Devuelve un dict con `memo` (markdown) y `orden_id`.
    """
    orden = context["orden"]

    validacion_raw = context["validacion"]
    validacion = (
        ValidacionReglas(**validacion_raw)
        if isinstance(validacion_raw, dict) else validacion_raw
    )

    analisis_raw = context["analisis"]
    analisis = (
        AnalisisContexto(**analisis_raw)
        if isinstance(analisis_raw, dict) else analisis_raw
    )

    clasificacion_raw = context["clasificacion"]
    clasificacion = (
        ClasificacionRiesgo(**clasificacion_raw)
        if isinstance(clasificacion_raw, dict) else clasificacion_raw
    )

    memo = _get_writer().redactar_memo(
        orden, validacion, analisis, clasificacion
    )
    return {"orden_id": orden["orden_id"], "memo": memo}