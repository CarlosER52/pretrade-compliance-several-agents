"""R2: Estrategia autorizada para el nivel del cliente."""

from src.rules.base import Rule
from src.schemas import ReglaResultado


ESTRATEGIAS_POR_NIVEL = {
    1: {"covered"},
    2: {"covered", "spread"},
    3: {"covered", "spread"},
    4: {"covered", "spread", "naked"},
    5: {"covered", "spread", "naked"},
}


class R2EstrategiaPermitida(Rule):
    regla_id = "R2_estrategia_permitida"

    def evaluar(self, orden: dict, contexto_cliente: dict) -> ReglaResultado:
        nivel = orden.get("nivel_aprobacion_cliente", 0)
        estrategia = orden.get("estrategia", "")
        permitidas = ESTRATEGIAS_POR_NIVEL.get(nivel, set())

        if estrategia not in permitidas:
            return ReglaResultado(
                regla_id=self.regla_id, resultado="fail",
                detalle=f"Estrategia {estrategia} no permitida para nivel {nivel}",
            )
        return ReglaResultado(
            regla_id=self.regla_id, resultado="pass",
            detalle=f"Estrategia {estrategia} permitida para nivel {nivel}",
        )