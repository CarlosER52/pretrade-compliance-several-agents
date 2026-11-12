"""Modelo del registro de auditoría."""

from datetime import datetime

from pydantic import BaseModel


class AuditTrail(BaseModel):
    orden_id: str
    artefactos: dict
    idempotency_key: str
    timestamp_archivado: datetime
