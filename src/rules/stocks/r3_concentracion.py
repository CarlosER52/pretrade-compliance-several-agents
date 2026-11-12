"""R3: Concentración sectorial (25% del capital)."""

from src.rules.base import Rule
from src.schemas import ReglaResultado


class R3Concentracion(Rule):
    regla_id = "R3_concentracion"
    LIMITE_PCT = 0.25

    def evaluar(self, orden: dict, contexto_cliente: dict) -> ReglaResultado:
        sector = orden.get("sector")
        if not sector:
            return ReglaResultado(
                regla_id=self.regla_id,
                resultado="pass",
                detalle="Sector no especificado; no se evalúa concentración",
                valor_observado=0.0,
                limite=self.LIMITE_PCT,
            )

        capital = contexto_cliente.get("capital_cuenta", 0)
        if capital <= 0:
            return ReglaResultado(
                regla_id=self.regla_id,
                resultado="fail",
                detalle="Capital de cuenta no disponible",
                valor_observado=capital,
                limite=self.LIMITE_PCT,
            )

        precio = orden.get("precio") or contexto_cliente.get(
            "precio_referencia", {}
        ).get(orden.get("simbolo"), 0)
        if not precio or precio <= 0:
            return ReglaResultado(
                regla_id=self.regla_id,
                resultado="fail",
                detalle="Precio no disponible para calcular concentración",
                valor_observado=precio,
                limite=self.LIMITE_PCT,
            )

        exposicion_sector = contexto_cliente.get("exposicion_sector", {}).get(
            sector, 0
        )
        valor_orden = orden["cantidad"] * precio
        exposicion_resultante = exposicion_sector + valor_orden
        ratio = exposicion_resultante / capital

        if ratio > self.LIMITE_PCT:
            return ReglaResultado(
                regla_id=self.regla_id,
                resultado="fail",
                detalle=(
                    f"Exposición sector {sector} {ratio:.2%} supera "
                    f"límite {self.LIMITE_PCT:.2%}"
                ),
                valor_observado=ratio,
                limite=self.LIMITE_PCT,
            )

        return ReglaResultado(
            regla_id=self.regla_id,
            resultado="pass",
            detalle=f"Exposición sector {sector} {ratio:.2%} OK",
            valor_observado=ratio,
            limite=self.LIMITE_PCT,
        )