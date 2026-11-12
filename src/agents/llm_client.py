"""Cliente LLM aislado con soporte para Z.ai, OpenRouter y Mock.

Estrategia:
- OpenAI (strict): usa Structured Outputs estricto (.parse()).
- Z.ai / OpenRouter (free): usan json_object + validación Pydantic manual.
- Mock: devuelve respuestas predefinidas sin llamada de red.

El resto del sistema solo llama a `parse_structured(...)` y no sabe
qué proveedor hay detrás.
"""

import json
import os
from typing import Type, TypeVar

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, ValidationError

# Cargar variables desde .env (si existe)
load_dotenv()

T = TypeVar("T", bound=BaseModel)


# Proveedores conocidos
_PROVIDERS = {
    "openai": {
        "base_url": None,  # el SDK usa el default
        "default_model": "gpt-4o-mini",
        "env_key": "OPENAI_API_KEY",
        "supports_strict": True,
    },
    "zai": {
        "base_url": "https://api.z.ai/api/paas/v4/",
        "default_model": "glm-4.7-flash",
        "env_key": "ZAI_API_KEY",
        "supports_strict": False,
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "default_model": "deepseek/deepseek-r1:free",
        "env_key": "OPENROUTER_API_KEY",
        "supports_strict": False,
    },
    "mock": {
        "base_url": None,
        "default_model": "mock",
        "env_key": None,
        "supports_strict": False,
    },
}


class LLMClient:
    """Cliente para llamadas LLM con salida estructurada."""

    def __init__(self, provider: str | None = None, model: str | None = None):
        provider = provider or os.getenv("LLM_PROVIDER", "openrouter")
        if provider not in _PROVIDERS:
            raise ValueError(
                f"Proveedor desconocido: {provider}. "
                f"Opciones: {list(_PROVIDERS.keys())}"
            )

        cfg = _PROVIDERS[provider]
        self.provider = provider
        self.supports_strict = cfg["supports_strict"]
        self.model = model or os.getenv("AGENT_MODEL", cfg["default_model"])

        if provider == "mock":
            self.client = None
            return

        env_key = cfg["env_key"]
        api_key = os.getenv(env_key) if env_key else None
        if not api_key:
            raise RuntimeError(
                f"{env_key} no configurada. Añádela a .env o exporta la variable."
            )

        kwargs = {"api_key": api_key}
        if cfg["base_url"]:
            kwargs["base_url"] = cfg["base_url"]
        self.client = OpenAI(**kwargs)

    def parse_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: Type[T],
        max_retries: int = 3,
    ) -> T:
        """Llama al LLM y devuelve una instancia de `response_model`.

        - OpenAI: Structured Outputs estricto.
        - Z.ai / OpenRouter: json_object + validación Pydantic.
        - Mock: respuesta predefinida.
        """
        if self.provider == "mock":
            return self._mock_response(response_model)

        if self.supports_strict:
            return self._parse_strict(
                system_prompt, user_prompt, response_model, max_retries
            )

        return self._parse_json_object(
            system_prompt, user_prompt, response_model, max_retries
        )

    # --- Mock ---

    def _mock_response(self, response_model: Type[T]) -> T:
        """Devuelve una respuesta predefinida que cumpla el schema."""
        # Intenta construir un AnalisisContexto genérico
        # (si el modelo no es AnalisisContexto, falla con un mensaje claro)
        try:
            return response_model(
                cliente_en_watchlist=False,
                patron_inusual=True,
                conflicto_politica=True,
                justificacion=(
                    "Mock: orden inusualmente grande y con fallo de posición. "
                    "El cliente no está en watchlist pero el patrón es atípico."
                ),
                confianza=0.9,
            )
        except Exception:
            raise ValueError(
                f"Mock solo soporta AnalisisContexto, no {response_model.__name__}"
            )

    # --- Modo estricto (OpenAI) ---

    def _parse_strict(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: Type[T],
        max_retries: int,
    ) -> T:
        last_error = None
        for _ in range(max_retries):
            try:
                completion = self.client.beta.chat.completions.parse(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    response_format=response_model,
                )
                message = completion.choices[0].message
                if message.refusal:
                    raise ValueError(f"Modelo rechazó: {message.refusal}")
                if message.parsed is None:
                    raise ValueError("Output no parseable")
                return message.parsed
            except Exception as e:
                last_error = e
        raise ValueError(f"LLM falló tras {max_retries} intentos: {last_error}")

    # --- Modo json_object + validación manual (Z.ai, OpenRouter) ---

    def _parse_json_object(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: Type[T],
        max_retries: int,
    ) -> T:
        # Inyectar el schema en el system prompt
        schema = response_model.model_json_schema()
        schema_str = json.dumps(schema, indent=2, ensure_ascii=False)
        system_with_schema = (
            f"{system_prompt}\n\n"
            f"Debes devolver ÚNICAMENTE un objeto JSON que cumpla "
            f"exactamente este JSON Schema:\n{schema_str}\n"
            f"No incluyas markdown, explicaciones ni texto adicional."
        )

        last_error = None
        for _ in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_with_schema},
                        {"role": "user", "content": user_prompt},
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.1,
                )
                raw = response.choices[0].message.content
                if not raw:
                    raise ValueError("Respuesta vacía")
                data = json.loads(raw)
                return response_model(**data)
            except (json.JSONDecodeError, ValidationError) as e:
                last_error = e
                continue
            except Exception as e:
                last_error = e
                continue
        raise ValueError(f"LLM falló tras {max_retries} intentos: {last_error}")