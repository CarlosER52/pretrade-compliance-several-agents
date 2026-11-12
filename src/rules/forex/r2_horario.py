"""R2: Horario de liquidación del par."""

from datetime import datetime, time

from src.rules.base import Rule
from src.schemas import ReglaResultado


# Ventanas de liquidación por par (hora UTC)
VENTANAS_LIQUIDACION = {
    "EUR/USD": (time(7, 0), time(16, 0)),
    "USD/JPY": (time(0, 0), time(8, 0)),
    "GBP/USD": (time(7, 0), time(16, 0)),
    "USD/CHF": (time(7, 0), time(16, 0)),
}


class R2HorarioLiquidacion(Rule):
    regla_id = "R2_horario_liquidacion"

    def evaluar(self, orden: dict, contexto_cliente: dict) -> ReglaResultado:
        par = orden.get("par")
        ventana = VENTANAS_LIQUIDACION.get(par)
        if ventana is None:
            return ReglaResultado(
                regla_id=self.regla_id, resultado="pass",
                detalle=f"Par {par} sin ventana definida; no se evalúa horario",
            )

        ts = orden.get("timestamp")
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts)
        elif ts is None:
            ts = datetime.utcnow()
        hora = ts.time()

        inicio, fin = ventana
        dentro = inicio <= hora <= fin
        if not dentro:
            return ReglaResultado(
                regla_id=self.regla_id, resultado="fail",
                detalle=f"Orden fuera de ventana de liquidación "
                        f"({inicio}-{fin} UTC), hora={hora}",
            )
        return ReglaResultado(
            regla_id=self.regla_id, resultado="pass",
            detalle=f"Dentro de ventana de liquidación ({inicio}-{fin} UTC)",
        )