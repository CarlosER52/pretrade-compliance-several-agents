"""Reglas duras para el instrumento futures."""

from src.rules.futures.r1_margen import R1Margen
from src.rules.futures.r2_limite_vencimiento import R2LimiteVencimiento
from src.rules.futures.r3_restriccion_roll import R3RestriccionRoll
from src.rules.futures.r4_limite_contratos import R4LimiteContratos
from src.rules.futures.r5_sesion import R5Sesion

__all__ = [
    "R1Margen", "R2LimiteVencimiento", "R3RestriccionRoll",
    "R4LimiteContratos", "R5Sesion",
]

REGLAS_FUTURES = [
    R1Margen(),
    R2LimiteVencimiento(),
    R3RestriccionRoll(),
    R4LimiteContratos(),
    R5Sesion(),
]