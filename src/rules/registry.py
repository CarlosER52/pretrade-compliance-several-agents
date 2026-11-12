"""Registro de reglas duras por instrumento."""

from src.schemas import ReglaResultado
from src.rules.stocks import REGLAS_STOCKS
from src.rules.forex import REGLAS_FOREX
from src.rules.crypto import REGLAS_CRYPTO
from src.rules.futures import REGLAS_FUTURES
from src.rules.options import REGLAS_OPTIONS


REGLAS_POR_INSTRUMENTO = {
    "stocks": REGLAS_STOCKS,
    "forex": REGLAS_FOREX,
    "crypto": REGLAS_CRYPTO,
    "futures": REGLAS_FUTURES,
    "options": REGLAS_OPTIONS,
}


def ejecutar_reglas_por_instrumento(
    orden: dict, contexto_cliente: dict
) -> list[ReglaResultado]:
    """Ejecuta las reglas duras del instrumento de la orden.

    Devuelve una lista de ReglaResultado (una por regla).
    Si el instrumento no tiene reglas registradas, devuelve lista vacía.
    """
    instrumento = orden.get("instrumento")
    reglas = REGLAS_POR_INSTRUMENTO.get(instrumento, [])
    resultados = []
    for regla in reglas:
        try:
            resultados.append(regla.evaluar(orden, contexto_cliente))
        except Exception as e:
            # Fail-safe: una regla que falla por error interno se trata
            # como fail (no se deja pasar la orden)
            resultados.append(
                ReglaResultado(
                    regla_id=getattr(regla, "regla_id", "desconocida"),
                    resultado="fail",
                    detalle=f"Error interno en regla: {e}",
                )
            )
    return resultados


def listar_reglas_por_instrumento() -> dict[str, list[str]]:
    """Devuelve un mapa instrumento -> lista de regla_ids."""
    return {
        inst: [r.regla_id for r in reglas]
        for inst, reglas in REGLAS_POR_INSTRUMENTO.items()
    }