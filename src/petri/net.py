"""Clases base de la red de Petri."""

from dataclasses import dataclass, field
from typing import Any, Callable, Optional

Token = Any


@dataclass
class Place:
    """Un lugar de la red. Puede ser de datos, recursos o control."""
    id: str
    type: str  # "data" | "resource" | "control"
    capacity: Optional[int] = None
    initial_tokens: int = 0
    tokens: list = field(default_factory=list)

    def __post_init__(self):
        if self.type == "resource" and self.initial_tokens:
            self.tokens = list(range(self.initial_tokens))
        if self.capacity is not None and len(self.tokens) > self.capacity:
            raise ValueError(f"Place {self.id}: tokens iniciales exceden capacity")

    def is_full(self) -> bool:
        return self.capacity is not None and len(self.tokens) >= self.capacity

    def can_add(self, n: int = 1) -> bool:
        if self.capacity is None:
            return True
        return len(self.tokens) + n <= self.capacity


@dataclass
class Transition:
    """Una transición con inputs, outputs, guarda determinista y acción."""
    id: str
    inputs: list  # [(place_id, cardinality)]
    outputs: list  # [(place_id, cardinality)]
    guard: Optional[Callable[..., tuple[bool, Any]]] = None
    action: Optional[Callable[..., Any]] = None


class PetriNet:
    """Red de Petri con método de disparo sincrónico."""

    def __init__(self) -> None:
        self.places = {}
        self.transitions = {}

    def add_place(self, place: Place) -> None:
        self.places[place.id] = place

    def add_transition(self, transition: Transition) -> None:
        self.transitions[transition.id] = transition

    def has_tokens(self, transition_id: str) -> bool:
        t = self.transitions[transition_id]
        return all(
            len(self.places[p].tokens) >= card for p, card in t.inputs
        )

    def fire(self, transition_id: str, context: Optional[dict] = None):
        """Intenta disparar una transición.

        Retorna (True, resultado) si disparó, (False, motivo) si no.
        """
        t = self.transitions[transition_id]
        if not self.has_tokens(transition_id):
            return False, "no_tokens"

        # Evaluar guarda antes de consumir
        if t.guard:
            ok, result = t.guard(context or {}, self.places)
            if not ok:
                return False, result

        # Consumir
        for place_id, card in t.inputs:
            place = self.places[place_id]
            for _ in range(card):
                place.tokens.pop(0)

        # Producir
        for place_id, card in t.outputs:
            place = self.places[place_id]
            if not place.can_add(card):
                raise RuntimeError(f"Place {place_id} excede capacity")
            for _ in range(card):
                place.tokens.append({"from": transition_id})

        # Ejecutar acción
        if t.action:
            result = t.action(context or {}, self.places)
        else:
            result = None

        return True, result
