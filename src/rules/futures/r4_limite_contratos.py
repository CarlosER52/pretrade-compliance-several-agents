"""R4: Límite de contratos por orden."""

from src.rules.base import Rule
from src.schemas import ReglaResultado


MAX_CONTRATOS_POR_ORDEN = 50


class R4LimiteContratos(Rule):
    regla_id = "R4_limite_contratos"

    def evaluar(self, orden: dict, contexto_cliente: dict) -> ReglaResultado:
        cantidad = orden["cantidad"]
        if cantidad > MAX_CONTRATOS_POR_ORDEN:
            return ReglaResultado(
                regla_id=self.regla_id, resultado="fail",
                detalle=f"Cantidad {cantidad} supera límite "
                        f"{MAX_CONTRATOS_POR_ORDEN}",
                valor_observado=cantidad, limite=MAX_CONTRATOS_POR_ORDEN,
            )
        return ReglaResultado(
            regla_id=self.regla_id, resultado="pass",
            detalle=f"Cantidad {cantidad} OK",
            valor_observado=cantidad, limite=MAX_CONTRATOS_POR_ORDEN,
        )