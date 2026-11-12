"""R5: Liquidez mínima del token (volumen 24h)."""

from src.rules.base import Rule
from src.schemas import ReglaResultado


# Volumen 24h simulado por token (USD)
VOLUMEN_24H = {
    "BTC": 25_000_000_000,
    "ETH": 12_000_000_000,
    "SOL": 2_500_000_000,
    "USDC": 5_000_000_000,
    "USDT": 40_000_000_000,
    "ADA": 800_000_000,
    "DOT": 400_000_000,
}

LIQUIDEZ_MINIMA = 1_000_000


class R5Liquidez(Rule):
    regla_id = "R5_liquidez"

    def evaluar(self, orden: dict, contexto_cliente: dict) -> ReglaResultado:
        token = orden.get("token", "").upper()
        volumen = VOLUMEN_24H.get(token, 0)
        if volumen < LIQUIDEZ_MINIMA:
            return ReglaResultado(
                regla_id=self.regla_id, resultado="fail",
                detalle=f"Liquidez de {token} ({volumen:,} USD) "
                        f"por debajo del mínimo ({LIQUIDEZ_MINIMA:,} USD)",
                valor_observado=volumen, limite=LIQUIDEZ_MINIMA,
            )
        return ReglaResultado(
            regla_id=self.regla_id, resultado="pass",
            detalle=f"Liquidez de {token} ({volumen:,} USD) OK",
            valor_observado=volumen, limite=LIQUIDEZ_MINIMA,
        )