"""Interfaz base para las reglas duras."""

from abc import ABC, abstractmethod

from src.schemas import ReglaResultado


class Rule(ABC):
    """Una regla dura determinista.

    Cada regla compara una métrica del orden/contexto contra un límite
    de política. Devuelve un ReglaResultado con pass/fail y detalle.
    """

    regla_id: str = ""

    @abstractmethod
    def evaluar(self, orden: dict, contexto_cliente: dict) -> ReglaResultado:
        """Evalúa la regla. No debe tener efectos secundarios."""
        ...