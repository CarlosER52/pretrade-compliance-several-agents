"""Modelo del artefacto de clasificación de riesgo."""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class ClasificacionRiesgo(BaseModel):
    orden_id: str
    riesgo: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    justificacion: str = Field(min_length=20)
    piso_aplicado: bool = False
    riesgo_sugerido_por_agente: Optional[str] = None
    hash_inputs: str
