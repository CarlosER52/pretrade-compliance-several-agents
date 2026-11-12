"""R5: Contraparte aprobada."""

from src.rules.base import Rule
from src.schemas import ReglaResultado


CONTRAPARTES_APROBADAS = {
    "BANK_A", "BANK_B", "BANK_C", "LP_XYZ", "LP_ABC",
}


class R5Contraparte(Rule):
    regla_id = "R5_contraparte"

    def evaluar(self, orden: dict, contexto_cliente: dict) -> ReglaResultado:
        contraparte = contexto_cliente.get("contraparte")
        if contraparte is None:
            return ReglaResultado(
                regla_id=self.regla_id, resultado="pass",
                detalle="Sin contraparte definida; no se evalúa",
            )
        if contraparte not in CONTRAPARTES_APROBADAS:
            return ReglaResultado(
                regla_id=self.regla_id, resultado="fail",
                detalle=f"Contraparte {contraparte} no aprobada",
            )
        return ReglaResultado(
            regla_id=self.regla_id, resultado="pass",
            detalle=f"Contraparte {contraparte} aprobada",
        )