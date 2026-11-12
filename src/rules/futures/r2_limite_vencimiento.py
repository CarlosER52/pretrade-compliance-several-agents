"""R2: Límite por vencimiento."""

from src.rules.base import Rule
from src.schemas import ReglaResultado


LIMITE_POR_VENCIMIENTO = 100  # contratos por vencimiento


class R2LimiteVencimiento(Rule):
    regla_id = "R2_limite_vencimiento"

    def evaluar(self, orden: dict, contexto_cliente: dict) -> ReglaResultado:
        vencimiento = orden.get("vencimiento", "")
        posicion_actual = contexto_cliente.get("posicion_vencimiento", {}).get(
            vencimiento, 0
        )
        posicion_resultante = posicion_actual + orden["cantidad"]

        if posicion_resultante > LIMITE_POR_VENCIMIENTO:
            return ReglaResultado(
                regla_id=self.regla_id, resultado="fail",
                detalle=f"Posición en vencimiento {vencimiento} "
                        f"({posicion_resultante}) supera límite "
                        f"({LIMITE_POR_VENCIMIENTO})",
                valor_observado=posicion_resultante,
                limite=LIMITE_POR_VENCIMIENTO,
            )
        return ReglaResultado(
            regla_id=self.regla_id, resultado="pass",
            detalle=f"Posición en vencimiento {posicion_resultante} OK",
            valor_observado=posicion_resultante,
            limite=LIMITE_POR_VENCIMIENTO,
        )