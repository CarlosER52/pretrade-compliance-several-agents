"""Reglas duras para el instrumento crypto."""

from src.rules.crypto.r1_activo_permitido import R1ActivoPermitido
from src.rules.crypto.r2_limite_exchange import R2LimiteExchange
from src.rules.crypto.r3_jurisdiccion import R3JurisdiccionCrypto
from src.rules.crypto.r4_watchlist_regulatoria import R4WatchlistRegulatoria
from src.rules.crypto.r5_liquidez import R5Liquidez

__all__ = [
    "R1ActivoPermitido", "R2LimiteExchange", "R3JurisdiccionCrypto",
    "R4WatchlistRegulatoria", "R5Liquidez",
]

REGLAS_CRYPTO = [
    R1ActivoPermitido(),
    R2LimiteExchange(),
    R3JurisdiccionCrypto(),
    R4WatchlistRegulatoria(),
    R5Liquidez(),
]