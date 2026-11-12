"""R5: Sesión de mercado abierta."""

from datetime import datetime, time

from src.rules.base import Rule
from src.schemas import ReglaResultado


# Sesiones por contrato (hora UTC)
SESIONES = {
    "ESZ6": (time(13, 30), time(20, 0)),
    "NQZ6": (time(13, 30), time(20, 0)),
    "CLZ6": (time(13, 0), time(19, 30)),
    "GCZ6": (time(13, 20), time(18, 30)),
}


class R5Sesion(Rule):
    regla_id = "R5_sesion"

    def evaluar(self, orden: dict, contexto_cliente: dict) -> ReglaResultado:
        contrato = orden.get("contrato", "")
        sesion = SESIONES.get(contrato)
        if sesion is None:
            return ReglaResultado(
                regla_id=self.regla_id, resultado="fail",
                detalle=f"Contrato {contrato} sin sesión definida",
            )

        ts = orden.get("timestamp")
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts)
        elif ts is None:
            ts = datetime.utcnow()
        hora = ts.time()

        inicio, fin = sesion
        if not (inicio <= hora <= fin):
            return ReglaResultado(
                regla_id=self.regla_id, resultado="fail",
                detalle=f"Fuera de sesión ({inicio}-{fin} UTC), hora={hora}",
            )
        return ReglaResultado(
            regla_id=self.regla_id, resultado="pass",
            detalle=f"Dentro de sesión ({inicio}-{fin} UTC)",
        )