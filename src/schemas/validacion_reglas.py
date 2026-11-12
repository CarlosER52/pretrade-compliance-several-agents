"""Modelo del artefacto de validación de reglas duras."""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class ReglaResultado(BaseModel):
    regla_id: str
    resultado: Literal["pass", "fail"]
    detalle: str
    valor_observado: Optional[float] = None
    limite: Optional[float] = None


class ValidacionReglas(BaseModel):
    orden_id: str
    instrumento: str
    reglas: list
    fallos_total: int = Field(ge=0)
    hash_inputs: str
