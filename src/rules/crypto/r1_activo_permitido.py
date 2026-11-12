"""R1: Token en lista permitida."""

from src.rules.base import Rule
from src.schemas import ReglaResultado


TOKENS_PERMITIDOS = {"BTC", "ETH", "SOL", "USDC", "USDT", "ADA", "DOT"}


class R1ActivoPermitido(Rule):
    regla_id = "R1_activo_permitido"

    def evaluar(self, orden: dict, contexto_cliente: dict) -> ReglaResultado:
        token = orden.get("token", "").upper()
        if token not in TOKENS_PERMITIDOS:
            return ReglaResultado(
                regla_id=self.regla_id, resultado="fail",
                detalle=f"Token {token} no está en la lista permitida",
            )
        return ReglaResultado(
            regla_id=self.regla_id, resultado="pass",
            detalle=f"Token {token} permitido",
        )