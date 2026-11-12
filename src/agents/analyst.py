"""Agente analista de contexto.

Produce un `AnalisisContexto` a partir de la orden y el resultado de
reglas duras. Es una función determinista con un LLM detrás: una sola
llamada, output validado contra schema, sin agencia autónoma.
"""

import json
from pathlib import Path

from src.agents.llm_client import LLMClient
from src.petri.transitions import calcular_hash
from src.schemas import AnalisisContexto, ValidacionReglas

# Cargar el prompt desde archivo (separado del código para auditoría)
_PROMPT_PATH = Path(__file__).parent / "prompts" / "analyst.md"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text(encoding="utf-8")


class AnalystAgent:
    """Agente analista de contexto con LLM."""

    def __init__(self, llm_client: LLMClient | None = None):
        self.llm = llm_client or LLMClient()

    def analizar(
        self,
        orden: dict,
        validacion: ValidacionReglas,
        contexto_cliente: dict,
    ) -> AnalisisContexto:
        """Analiza el contexto de la orden y devuelve un AnalisisContexto."""
        user_prompt = self._build_user_prompt(orden, validacion, contexto_cliente)

        analisis_llm = self.llm.parse_structured(
            system_prompt=_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=AnalisisContexto,
        )

        # Rellenar campos que el LLM no debe inventar (trazabilidad)
        analisis_llm.orden_id = orden["orden_id"]
        analisis_llm.hash_inputs = calcular_hash(orden)

        return analisis_llm

    def _build_user_prompt(
        self,
        orden: dict,
        validacion: ValidacionReglas,
        contexto_cliente: dict,
    ) -> str:
        """Construye el prompt con los datos de la orden y el contexto.

        Nota: NO usamos backticks triples dentro del f-string porque
        rompen el parser en algunos editores. Usamos separadores '---'.
        """
        orden_json = json.dumps(orden, indent=2, ensure_ascii=False, default=str)
        validacion_json = json.dumps(
            validacion.model_dump(), indent=2, ensure_ascii=False, default=str
        )
        contexto_json = json.dumps(
            contexto_cliente, indent=2, ensure_ascii=False, default=str
        )

        partes = [
            "Analiza el contexto de la siguiente orden.",
            "",
            "--- ORDEN PROPUESTA ---",
            orden_json,
            "",
            "--- RESULTADO DE REGLAS DURAS ---",
            validacion_json,
            "",
            "--- CONTEXTO DEL CLIENTE ---",
            contexto_json,
            "",
            "Produce el análisis estructurado según el schema solicitado.",
        ]
        return "\n".join(partes)


# ------------------------------------------------------------
# Wrapper para el motor de Petri
# ------------------------------------------------------------

_analyst_agent: AnalystAgent | None = None


def _get_agent() -> AnalystAgent:
    global _analyst_agent
    if _analyst_agent is None:
        _analyst_agent = AnalystAgent()
    return _analyst_agent


def analyst_agent_action(context: dict, places: dict) -> dict:
    """Acción de la transición `t_ejecutar_analisis`.

    Requiere en `context`:
        - `orden`: dict.
        - `validacion`: ValidacionReglas (o dict compatible).
        - `contexto_cliente`: dict.

    Devuelve el AnalisisContexto serializado como dict.
    """
    orden = context["orden"]
    validacion_raw = context["validacion"]

    if isinstance(validacion_raw, dict):
        validacion = ValidacionReglas(**validacion_raw)
    else:
        validacion = validacion_raw

    contexto_cliente = context.get("contexto_cliente", {})

    analisis = _get_agent().analizar(orden, validacion, contexto_cliente)
    return analisis.model_dump()