"""R2: Límite de exposición por exchange (30% del capital)."""

from src.rules.base import Rule
from src.schemas import ReglaResultado


class R2LimiteExchange(Rule):
    regla_id = "R2_limite_exchange"
    LIMITE_PCT = 0.30

    def evaluar(self, orden: dict, contexto_cliente: dict) -> ReglaResultado:
        capital = contexto_cliente.get("capital_cuenta", 0)
        if capital <= 0:
            return ReglaResultado(
                regla_id=self.regla_id, resultado="fail",
                detalle="Capital no disponible",
                valor_observado=capital, limite=self.LIMITE_PCT,
            )

        exchange = orden.get("exchange", "")
        precio = orden.get("precio") or contexto_cliente.get(
            "precio_referencia", {}
        ).get(orden.get("token"), 0)
        if not precio or precio <= 0:
            return ReglaResultado(
                regla_id=self.regla_id, resultado="fail",
                detalle="Precio no disponible",
                valor_observado=precio, limite=self.LIMITE_PCT,
            )

        exposicion_actual = contexto_cliente.get("exposicion_exchange", {}).get(
            exchange, 0
        )
        valor_orden = orden["cantidad"] * precio
        exposicion_resultante = exposicion_actual + valor_orden
        ratio = exposicion_resultante / capital

        if ratio > self.LIMITE_PCT:
            return ReglaResultado(
                regla_id=self.regla_id, resultado="fail",
                detalle=f"Exposición exchange {exchange} {ratio:.2%} "
                        f"supera límite {self.LIMITE_PCT:.2%}",
                valor_observado=ratio, limite=self.LIMITE_PCT,
            )
        return ReglaResultado(
            regla_id=self.regla_id, resultado="pass",
            detalle=f"Exposición exchange {exchange} {ratio:.2%} OK",
            valor_observado=ratio, limite=self.LIMITE_PCT,
        )