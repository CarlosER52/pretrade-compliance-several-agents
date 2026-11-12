"""Modelo del acta de decisión del oficial humano."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ActaCompliance(BaseModel):
    orden_id: str
    decision: Literal["aprobada", "rechazada"]
    oficial: str
    firma: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    justificacion: str = Field(min_length=20)
    hash_clasificacion: str
