"""R4: Exposición correlacionada (40% del capital)."""

from src.rules.base import Rule
from src.schemas import ReglaResultado


# Pares correlacionados (grupos)
GRUPOS_CORRELACION = [
    {"EUR/USD", "GBP/USD", "AUD/USD"},  # USD como cotizada
    {"USD/JPY", "USD/CHF", "USD/CAD"},  # USD como base
]


class R4Correlacion(Rule):
    regla_id = "R4_correlacion"
    LIMITE_PCT = 0.40

    def evaluar(self, orden: dict, contexto_cliente: dict) -> ReglaResultado:
        par = orden.get("par")
        capital = contexto_cliente.get("capital_cuenta", 0)
        if capital <= 0:
            return ReglaResultado(
                regla_id=self.regla_id, resultado="fail",
                detalle="Capital no disponible",
                valor_observado=capital, limite=self.LIMITE_PCT,
            )

        # Encontrar grupo del par
        grupo = None
        for g in GRUPOS_CORRELACION:
            if par in g:
                grupo = g
                break
        if grupo is None:
            return ReglaResultado(
                regla_id=self.regla_id, resultado="pass",
                detalle=f"Par {par} sin grupo de correlación definido",
            )

        # Sumar exposición de todos los pares del grupo
        exposicion_par = contexto_cliente.get("exposicion_par", {})
        exposicion_total = sum(exposicion_par.get(p, 0) for p in grupo)

        tasa = orden.get("tasa") or contexto_cliente.get(
            "tasa_referencia", {}
        ).get(par, 0)
        valor_orden = orden["cantidad"] * (tasa or 0)
        exposicion_resultante = exposicion_total + valor_orden
        ratio = exposicion_resultante / capital

        if ratio > self.LIMITE_PCT:
            return ReglaResultado(
                regla_id=self.regla_id, resultado="fail",
                detalle=f"Exposición correlacionada {ratio:.2%} "
                        f"supera límite {self.LIMITE_PCT:.2%}",
                valor_observado=ratio, limite=self.LIMITE_PCT,
            )
        return ReglaResultado(
            regla_id=self.regla_id, resultado="pass",
            detalle=f"Exposición correlacionada {ratio:.2%} OK",
            valor_observado=ratio, limite=self.LIMITE_PCT,
        )