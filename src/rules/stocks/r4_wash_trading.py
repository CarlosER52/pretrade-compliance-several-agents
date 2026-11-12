"""R4: Patrón de wash trading."""

from src.rules.base import Rule
from src.schemas import ReglaResultado


class R4WashTrading(Rule):
    regla_id = "R4_wash_trading"

    def evaluar(self, orden: dict, contexto_cliente: dict) -> ReglaResultado:
        cliente_id = orden.get("cliente_id")
        contra_partida = contexto_cliente.get("contra_partida_cliente_id")

        if contra_partida is None:
            # No hay contra-partida conocida: no se puede evaluar
            return ReglaResultado(
                regla_id=self.regla_id,
                resultado="pass",
                detalle="Sin contra-partida; no se detecta wash trading",
                valor_observado=0.0,
                limite=0.0,
            )

        if contra_partida == cliente_id:
            return ReglaResultado(
                regla_id=self.regla_id,
                resultado="fail",
                detalle=(
                    f"Cliente {cliente_id} opera contra sí mismo "
                    f"(contra-partida {contra_partida})"
                ),
                valor_observado=1.0,
                limite=0.0,
            )

        return ReglaResultado(
            regla_id=self.regla_id,
            resultado="pass",
            detalle="Sin patrón de wash trading",
            valor_observado=0.0,
            limite=0.0,
        )