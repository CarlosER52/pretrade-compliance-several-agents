"""R1: Nivel de aprobación del cliente suficiente."""

from src.rules.base import Rule
from src.schemas import ReglaResultado


# Nivel mínimo requerido por estrategia
NIVEL_REQUERIDO = {"covered": 1, "spread": 2, "naked": 4}


class R1NivelAprobacion(Rule):
    regla_id = "R1_nivel_aprobacion"

    def evaluar(self, orden: dict, contexto_cliente: dict) -> ReglaResultado:
        estrategia = orden.get("estrategia", "")
        nivel_cliente = orden.get("nivel_aprobacion_cliente", 0)
        requerido = NIVEL_REQUERIDO.get(estrategia)

        if requerido is None:
            return ReglaResultado(
                regla_id=self.regla_id, resultado="fail",
                detalle=f"Estrategia {estrategia} desconocida",
            )
        if nivel_cliente < requerido:
            return ReglaResultado(
                regla_id=self.regla_id, resultado="fail",
                detalle=f"Nivel {nivel_cliente} < requerido {requerido} "
                        f"para estrategia {estrategia}",
                valor_observado=nivel_cliente, limite=requerido,
            )
        return ReglaResultado(
            regla_id=self.regla_id, resultado="pass",
            detalle=f"Nivel {nivel_cliente} OK (requerido {requerido})",
            valor_observado=nivel_cliente, limite=requerido,
        )