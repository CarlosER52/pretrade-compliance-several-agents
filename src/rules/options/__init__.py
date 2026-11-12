"""Reglas duras para el instrumento options."""

from src.rules.options.r1_nivel_aprobacion import R1NivelAprobacion
from src.rules.options.r2_estrategia_permitida import R2EstrategiaPermitida
from src.rules.options.r3_limite_griegas import R3LimiteGriegas
from src.rules.options.r4_naked_put import R4NakedPut
from src.rules.options.r5_vencimiento import R5Vencimiento

__all__ = [
    "R1NivelAprobacion", "R2EstrategiaPermitida", "R3LimiteGriegas",
    "R4NakedPut", "R5Vencimiento",
]

REGLAS_OPTIONS = [
    R1NivelAprobacion(),
    R2EstrategiaPermitida(),
    R3LimiteGriegas(),
    R4NakedPut(),
    R5Vencimiento(),
]