"""R1: Margen disponible."""

from src.rules.base import Rule
from src.schemas import ReglaResultado


# Margen requerido por contrato (simulado)
MARGEN_POR_CONTRATO = {
    "ESZ6": 15_000, "NQZ6": 20_000, "CLZ6": 5_000, "GCZ6": 8_000,
}


class R1Margen(Rule):
    regla_id = "R1_margen"

    def evaluar(self, orden: dict, contexto_cliente: dict) -> ReglaResultado:
        contrato = orden.get("contrato", "")
        margen_req = MARGEN_POR_CONTRATO.get(contrato)
        if margen_req is None:
            return ReglaResultado(
                regla_id=self.regla_id, resultado="fail",
                detalle=f"Contrato {contrato} sin margen definido",
            )

        margen_requerido_total = margen_req * orden["cantidad"]
        margen_disponible = orden.get("margen_disponible", 0)

        if margen_requerido_total > margen_disponible:
            return ReglaResultado(
                regla_id=self.regla_id, resultado="fail",
                detalle=f"Margen requerido {margen_requerido_total:,} > "
                        f"disponible {margen_disponible:,}",
                valor_observado=margen_requerido_total,
                limite=margen_disponible,
            )
        return ReglaResultado(
            regla_id=self.regla_id, resultado="pass",
            detalle=f"Margen requerido {margen_requerido_total:,} OK",
            valor_observado=margen_requerido_total,
            limite=margen_disponible,
        )