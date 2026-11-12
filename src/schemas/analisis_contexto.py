"""Modelo del artefacto de análisis de contexto por agente."""

from pydantic import BaseModel, Field


class AnalisisContexto(BaseModel):
    orden_id: str
    cliente_en_watchlist: bool
    patron_inusual: bool
    conflicto_politica: bool
    justificacion: str = Field(min_length=20)
    confianza: float = Field(ge=0.0, le=1.0)
    hash_inputs: str
