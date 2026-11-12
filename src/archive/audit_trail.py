"""Archivado idempotente del audit trail."""

import hashlib
import json
from datetime import datetime
from pathlib import Path

from src.schemas import AuditTrail


_ARCHIVE_DIR = Path(__file__).parent.parent.parent / "archive_store"


def _idempotency_key(orden_id: str, timestamp_decision: str) -> str:
    raw = f"{orden_id}:{timestamp_decision}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def validar_archivo(context: dict, places: dict) -> tuple[bool, str]:
    """Guarda de t_archivar: verifica idempotencia y trazabilidad."""
    acta = context.get("acta")
    if not acta:
        return False, "acta_ausente"

    orden_id = acta["orden_id"]
    ts = acta["timestamp"]
    key = _idempotency_key(orden_id, str(ts))

    # Si ya existe, no re-archivar
    archive_file = _ARCHIVE_DIR / f"{orden_id}.json"
    if archive_file.exists():
        return False, "ya_archivado(idempotente)"

    # Trazabilidad: el acta debe referenciar la clasificación
    if not acta.get("hash_clasificacion"):
        return False, "acta_sin_hash_clasificacion"

    return True, "OK"


def archivar_action(context: dict, places: dict) -> dict:
    """Acción de t_archivar. Persiste el audit trail en disco."""
    acta = context["acta"]
    orden_id = acta["orden_id"]
    key = _idempotency_key(orden_id, str(acta["timestamp"]))

    audit = AuditTrail(
        orden_id=orden_id,
        artefactos=context.get("artefactos", {}),
        idempotency_key=key,
        timestamp_archivado=datetime.utcnow(),
    )

    _ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    archive_file = _ARCHIVE_DIR / f"{orden_id}.json"
    archive_file.write_text(
        audit.model_dump_json(indent=2), encoding="utf-8"
    )

    return audit.model_dump()