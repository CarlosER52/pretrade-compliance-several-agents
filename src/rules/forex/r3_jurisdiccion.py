"""R3: Restricción de jurisdicción del cliente."""

from src.rules.base import Rule
from src.schemas import ReglaResultado


# Pares restringidos por jurisdicción del cliente
JURISDICCIONES_RESTRINGIDAS = {
    "EUR/USD": {"US", "IR", "KP"},
    "USD/JPY": {"IR", "KP"},
    "GBP/USD": {"IR", "KP"},
    "USD/CHF": {"IR", "KP"},
}


class R3Jurisdiccion(Rule):
    regla_id = "R3_jurisdiccion"

    def evaluar(self, orden: dict, contexto_cliente: dict) -> ReglaResultado:
        par = orden.get("par")
        jurisdiccion = orden.get("jurisdiccion_cliente") or \
            contexto_cliente.get("jurisdiccion_cliente", "")

        restringidas = JURISDICCIONES_RESTRINGIDAS.get(par, set())
        if jurisdiccion in restringidas:
            return ReglaResultado(
                regla_id=self.regla_id, resultado="fail",
                detalle=f"Jurisdicción {jurisdiccion} restringida para par {par}",
            )
        return ReglaResultado(
            regla_id=self.regla_id, resultado="pass",
            detalle=f"Jurisdicción {jurisdiccion or 'N/A'} OK para par {par}",
        )