"""R5: Sectores prohibidos."""

from src.rules.base import Rule
from src.schemas import ReglaResultado


SECTORES_PROHIBIDOS = {"tabaco", "armas_controvertidas", "juego"}


class R5Sector(Rule):
    regla_id = "R5_sector"

    def evaluar(self, orden: dict, contexto_cliente: dict) -> ReglaResultado:
        sector = (orden.get("sector") or "").lower()
        if sector in SECTORES_PROHIBIDOS:
            return ReglaResultado(
                regla_id=self.regla_id,
                resultado="fail",
                detalle=f"Sector {sector} está en lista de prohibidos",
                valor_observado=1.0,
                limite=0.0,
            )
        return ReglaResultado(
            regla_id=self.regla_id,
            resultado="pass",
            detalle=f"Sector {sector or 'N/A'} no está prohibido",
            valor_observado=0.0,
            limite=0.0,
        )