"""R1: Límite de posición por emisor (10% del capital)."""

from src.rules.base import Rule
from src.schemas import ReglaResultado


class R1Posicion(Rule):
    regla_id = "R1_posicion"
    LIMITE_PCT = 0.10

    def evaluar(self, orden: dict, contexto_cliente: dict) -> ReglaResultado:
        capital = contexto_cliente.get("capital_cuenta", 0)
        if capital <= 0:
            return ReglaResultado(
                regla_id=self.regla_id,
                resultado="fail",
                detalle="Capital de cuenta no disponible o inválido",
                valor_observado=capital,
                limite=self.LIMITE_PCT,
            )

        precio = orden.get("precio")
        if precio is None:
            # Market order: usamos un precio de referencia del contexto
            precio = contexto_cliente.get("precio_referencia", {}).get(
                orden.get("simbolo"), 0
            )
        if not precio or precio <= 0:
            return ReglaResultado(
                regla_id=self.regla_id,
                resultado="fail",
                detalle="Precio no disponible para calcular posición",
                valor_observado=precio,
                limite=self.LIMITE_PCT,
            )

        posicion_actual = contexto_cliente.get("posicion_actual", {}).get(
            orden.get("simbolo"), 0
        )
        valor_orden = orden["cantidad"] * precio
        posicion_resultante = posicion_actual + valor_orden
        ratio = posicion_resultante / capital

        if ratio > self.LIMITE_PCT:
            return ReglaResultado(
                regla_id=self.regla_id,
                resultado="fail",
                detalle=(
                    f"Posición resultante {ratio:.2%} supera límite "
                    f"{self.LIMITE_PCT:.2%}"
                ),
                valor_observado=ratio,
                limite=self.LIMITE_PCT,
            )

        return ReglaResultado(
            regla_id=self.regla_id,
            resultado="pass",
            detalle=f"Posición resultante {ratio:.2%} dentro del límite",
            valor_observado=ratio,
            limite=self.LIMITE_PCT,
        )