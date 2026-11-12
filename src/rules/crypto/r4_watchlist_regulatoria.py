"""R4: Token en watchlist regulatoria."""

from src.rules.base import Rule
from src.schemas import ReglaResultado


WATCHLIST_REGULATORIA = {"XRP", "TRX", "XMR", "ZEC"}


class R4WatchlistRegulatoria(Rule):
    regla_id = "R4_watchlist_regulatoria"

    def evaluar(self, orden: dict, contexto_cliente: dict) -> ReglaResultado:
        token = orden.get("token", "").upper()
        if token in WATCHLIST_REGULATORIA:
            return ReglaResultado(
                regla_id=self.regla_id, resultado="fail",
                detalle=f"Token {token} en watchlist regulatoria",
            )
        return ReglaResultado(
            regla_id=self.regla_id, resultado="pass",
            detalle=f"Token {token} no está en watchlist regulatoria",
        )