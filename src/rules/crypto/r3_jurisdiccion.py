"""R3: Jurisdicción del cliente para el token."""

from src.rules.base import Rule
from src.schemas import ReglaResultado


JURISDICCIONES_PERMITIDAS = {
    "BTC": {"US", "EU", "UK", "JP", "SG"},
    "ETH": {"US", "EU", "UK", "JP", "SG"},
    "SOL": {"US", "EU", "SG"},
    "USDC": {"US", "EU", "UK", "JP", "SG"},
    "USDT": {"US", "EU", "SG"},
    "ADA": {"EU", "SG"},
    "DOT": {"EU", "SG"},
}


class R3JurisdiccionCrypto(Rule):
    regla_id = "R3_jurisdiccion"

    def evaluar(self, orden: dict, contexto_cliente: dict) -> ReglaResultado:
        token = orden.get("token", "").upper()
        jurisdiccion = orden.get("jurisdiccion_cliente") or \
            contexto_cliente.get("jurisdiccion_cliente", "")

        permitidas = JURISDICCIONES_PERMITIDAS.get(token, set())
        if jurisdiccion not in permitidas:
            return ReglaResultado(
                regla_id=self.regla_id, resultado="fail",
                detalle=f"Jurisdicción {jurisdiccion} no permitida para {token}",
            )
        return ReglaResultado(
            regla_id=self.regla_id, resultado="pass",
            detalle=f"Jurisdicción {jurisdiccion} OK para {token}",
        )