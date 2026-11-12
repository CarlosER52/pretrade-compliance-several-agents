"""Reglas duras para el instrumento forex."""

from src.rules.forex.r1_exposicion_par import R1ExposicionPar
from src.rules.forex.r2_horario import R2HorarioLiquidacion
from src.rules.forex.r3_jurisdiccion import R3Jurisdiccion
from src.rules.forex.r4_correlacion import R4Correlacion
from src.rules.forex.r5_contraparte import R5Contraparte

__all__ = [
    "R1ExposicionPar", "R2HorarioLiquidacion", "R3Jurisdiccion",
    "R4Correlacion", "R5Contraparte",
]

REGLAS_FOREX = [
    R1ExposicionPar(),
    R2HorarioLiquidacion(),
    R3Jurisdiccion(),
    R4Correlacion(),
    R5Contraparte(),
]