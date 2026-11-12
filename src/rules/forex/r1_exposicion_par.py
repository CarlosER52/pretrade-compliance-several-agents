"""R1: Exposición por par (20% del capital)."""

from src.rules.base import Rule
from src.schemas import ReglaResultado


class R1ExposicionPar(Rule):
    regla_id = "R1_exposicion_par"
    LIMITE_PCT = 0.20

    def evaluar(self, orden: dict, contexto_cliente: dict) -> ReglaResultado:
        capital = contexto_cliente.get("capital_cuenta", 0)
        if capital <= 0:
            return ReglaResultado(
                regla_id=self.regla_id, resultado="fail",
                detalle="Capital de cuenta no disponible",
                valor_observado=capital, limite=self.LIMITE_PCT,
            )

        tasa = orden.get("tasa") or contexto_cliente.get(
            "tasa_referencia", {}
        ).get(orden.get("par"), 0)
        if not tasa or tasa <= 0:
            return ReglaResultado(
                regla_id=self.regla_id, resultado="fail",
                detalle="Tasa no disponible para calcular exposición",
                valor_observado=tasa, limite=self.LIMITE_PCT,
            )

        exposicion_actual = contexto_cliente.get("exposicion_par", {}).get(
            orden.get("par"), 0
        )
        valor_orden = orden["cantidad"] * tasa
        exposicion_resultante = exposicion_actual + valor_orden
        ratio = exposicion_resultante / capital

        if ratio > self.LIMITE_PCT:
            return ReglaResultado(
                regla_id=self.regla_id, resultado="fail",
                detalle=f"Exposición par {orden.get('par')} {ratio:.2%} "
                        f"supera límite {self.LIMITE_PCT:.2%}",
                valor_observado=ratio, limite=self.LIMITE_PCT,
            )
        return ReglaResultado(
            regla_id=self.regla_id, resultado="pass",
            detalle=f"Exposición par {ratio:.2%} OK",
            valor_observado=ratio, limite=self.LIMITE_PCT,
        )