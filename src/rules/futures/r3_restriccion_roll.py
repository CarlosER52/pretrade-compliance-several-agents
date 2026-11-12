"""R3: Restricción de roll."""

from src.rules.base import Rule
from src.schemas import ReglaResultado


CONTRATOS_CON_ROLL_PERMITIDO = {"ESZ6", "NQZ6", "CLZ6", "GCZ6"}


class R3RestriccionRoll(Rule):
    regla_id = "R3_restriccion_roll"

    def evaluar(self, orden: dict, contexto_cliente: dict) -> ReglaResultado:
        es_roll = contexto_cliente.get("es_roll", False)
        if not es_roll:
            return ReglaResultado(
                regla_id=self.regla_id, resultado="pass",
                detalle="No es roll; no se evalúa",
            )

        contrato = orden.get("contrato", "")
        if contrato not in CONTRATOS_CON_ROLL_PERMITIDO:
            return ReglaResultado(
                regla_id=self.regla_id, resultado="fail",
                detalle=f"Roll no permitido para contrato {contrato}",
            )
        return ReglaResultado(
            regla_id=self.regla_id, resultado="pass",
            detalle=f"Roll permitido para contrato {contrato}",
        )