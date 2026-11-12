"""R4: Naked put requiere nivel 4+."""

from src.rules.base import Rule
from src.schemas import ReglaResultado


class R4NakedPut(Rule):
    regla_id = "R4_naked_put"

    def evaluar(self, orden: dict, contexto_cliente: dict) -> ReglaResultado:
        estrategia = orden.get("estrategia", "")
        tipo_opcion = orden.get("tipo_opcion", "")
        nivel = orden.get("nivel_aprobacion_cliente", 0)

        if estrategia == "naked" and tipo_opcion == "put":
            if nivel < 4:
                return ReglaResultado(
                    regla_id=self.regla_id, resultado="fail",
                    detalle=f"Naked put requiere nivel 4+, cliente tiene {nivel}",
                    valor_observado=nivel, limite=4,
                )
        return ReglaResultado(
            regla_id=self.regla_id, resultado="pass",
            detalle="No es naked put o nivel suficiente",
        )