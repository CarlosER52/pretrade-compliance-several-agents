"""R5: Vencimiento mínimo de la opción.

Una opción con muy pocos días al vencimiento tiene riesgo de expiración
inminente y poca liquidez. La política interna exige al menos 7 días.
"""

from datetime import date, datetime

from src.rules.base import Rule
from src.schemas import ReglaResultado


MIN_DIAS_VENCIMIENTO = 7


class R5Vencimiento(Rule):
    regla_id = "R5_vencimiento"

    def evaluar(self, orden: dict, contexto_cliente: dict) -> ReglaResultado:
        vencimiento_raw = orden.get("vencimiento")
        if not vencimiento_raw:
            return ReglaResultado(
                regla_id=self.regla_id,
                resultado="fail",
                detalle="Vencimiento no especificado en la orden",
            )

        # Parsear vencimiento (acepta date, datetime o string ISO)
        try:
            if isinstance(vencimiento_raw, datetime):
                vencimiento = vencimiento_raw.date()
            elif isinstance(vencimiento_raw, date):
                vencimiento = vencimiento_raw
            else:
                vencimiento = date.fromisoformat(str(vencimiento_raw))
        except (ValueError, TypeError) as e:
            return ReglaResultado(
                regla_id=self.regla_id,
                resultado="fail",
                detalle=f"Vencimiento inválido: {vencimiento_raw} ({e})",
            )

        # Fecha de referencia: timestamp de la orden o hoy
        ts = orden.get("timestamp")
        if isinstance(ts, str):
            try:
                fecha_ref = datetime.fromisoformat(ts).date()
            except ValueError:
                fecha_ref = date.today()
        elif isinstance(ts, datetime):
            fecha_ref = ts.date()
        elif isinstance(ts, date):
            fecha_ref = ts
        else:
            fecha_ref = date.today()

        dias_al_vencimiento = (vencimiento - fecha_ref).days

        if dias_al_vencimiento < MIN_DIAS_VENCIMIENTO:
            return ReglaResultado(
                regla_id=self.regla_id,
                resultado="fail",
                detalle=(
                    f"Vencimiento en {dias_al_vencimiento} días, "
                    f"mínimo requerido {MIN_DIAS_VENCIMIENTO}"
                ),
                valor_observado=float(dias_al_vencimiento),
                limite=float(MIN_DIAS_VENCIMIENTO),
            )

        return ReglaResultado(
            regla_id=self.regla_id,
            resultado="pass",
            detalle=(
                f"Vencimiento en {dias_al_vencimiento} días "
                f"(mínimo {MIN_DIAS_VENCIMIENTO})"
            ),
            valor_observado=float(dias_al_vencimiento),
            limite=float(MIN_DIAS_VENCIMIENTO),
        )