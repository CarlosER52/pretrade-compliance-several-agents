"""Reglas duras para el instrumento stocks."""

from src.rules.stocks.r1_posicion import R1Posicion
from src.rules.stocks.r2_lista import R2ListaRestringida
from src.rules.stocks.r3_concentracion import R3Concentracion
from src.rules.stocks.r4_wash_trading import R4WashTrading
from src.rules.stocks.r5_sector import R5Sector

__all__ = [
    "R1Posicion",
    "R2ListaRestringida",
    "R3Concentracion",
    "R4WashTrading",
    "R5Sector",
]

# Lista ordenada de reglas para stocks
REGLAS_STOCKS = [
    R1Posicion(),
    R2ListaRestringida(),
    R3Concentracion(),
    R4WashTrading(),
    R5Sector(),
]