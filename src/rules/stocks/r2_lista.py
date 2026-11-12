"""R2: Emisor en lista de restricción."""

from src.rules.base import Rule
from src.schemas import ReglaResultado


# Lista ficticia de emisores restringidos (en producción vendría de una
# fuente externa o base de datos de compliance)
LISTA_RESTRINGIDA = {"GME", "AMC", "BBBY"}


class R2ListaRestringida(Rule):
    regla_id = "R2_lista_restringida"

    def evaluar(self, orden: dict, contexto_cliente: dict) -> ReglaResultado:
        simbolo = orden.get("simbolo", "")
        if simbolo in LISTA_RESTRINGIDA:
            return ReglaResultado(
                regla_id=self.regla_id,
                resultado="fail",
                detalle=f"Emisor {simbolo} está en lista de restricción",
                valor_observado=1.0,
                limite=0.0,
            )
        return ReglaResultado(
            regla_id=self.regla_id,
            resultado="pass",
            detalle=f"Emisor {simbolo} no está restringido",
            valor_observado=0.0,
            limite=0.0,
        )