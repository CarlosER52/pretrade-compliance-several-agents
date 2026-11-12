"""R3: Límite de griegas (delta)."""

from src.rules.base import Rule
from src.schemas import ReglaResultado


LIMITE_DELTA = 500.0


class R3LimiteGriegas(Rule):
    regla_id = "R3_limite_griegas"

    def evaluar(self, orden: dict, contexto_cliente: dict) -> ReglaResultado:
        delta_orden = orden.get("delta_orden") or contexto_cliente.get(
            "delta_orden", 0
        )
        delta_actual = contexto_cliente.get("delta_total", 0)
        delta_resultante = delta_actual + delta_orden

        if abs(delta_resultante) > LIMITE_DELTA:
            return ReglaResultado(
                regla_id=self.regla_id, resultado="fail",
                detalle=f"Delta resultante {delta_resultante:.2f} "
                        f"supera límite ±{LIMITE_DELTA}",
                valor_observado=delta_resultante, limite=LIMITE_DELTA,
            )
        return ReglaResultado(
            regla_id=self.regla_id, resultado="pass",
            detalle=f"Delta {delta_resultante:.2f} OK",
            valor_observado=delta_resultante, limite=LIMITE_DELTA,
        )