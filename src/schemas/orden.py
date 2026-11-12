"""Modelos de orden por instrumento."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class OrdenBase(BaseModel):
    orden_id: str = Field(pattern=r"^ORD-\d{4}-\d{2}-\d{5}$")
    instrumento: Literal["stocks", "forex", "crypto", "futures", "options"]
    tipo: Literal["buy", "sell"]
    cantidad: float = Field(gt=0)
    cuenta_id: str
    cliente_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class OrdenStocks(OrdenBase):
    instrumento: Literal["stocks"]
    simbolo: str
    precio: Optional[float] = Field(default=None, gt=0)
    tipo_orden: Literal["market", "limit"] = "market"
    sector: Optional[str] = None


class OrdenForex(OrdenBase):
    instrumento: Literal["forex"]
    par: str
    tasa: Optional[float] = Field(default=None, gt=0)
    jurisdiccion_cliente: str


class OrdenCrypto(OrdenBase):
    instrumento: Literal["crypto"]
    token: str
    exchange: str
    precio: Optional[float] = None
    jurisdiccion_cliente: str


class OrdenFutures(OrdenBase):
    instrumento: Literal["futures"]
    contrato: str
    vencimiento: str
    margen_disponible: float = Field(ge=0)
    precio: Optional[float] = None


class OrdenOptions(OrdenBase):
    instrumento: Literal["options"]
    subyacente: str
    tipo_opcion: Literal["call", "put"]
    strike: float = Field(gt=0)
    vencimiento: str
    nivel_aprobacion_cliente: int = Field(ge=1, le=5)
    estrategia: Literal["covered", "naked", "spread"]
