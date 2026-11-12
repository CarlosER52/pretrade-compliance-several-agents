"""Motor de disparo de la red de Petri.

Reexporta PetriNet para conveniencia. La lógica de disparo vive en
src/petri/net.py.
"""

from src.petri.net import PetriNet, Place, Transition

__all__ = ["PetriNet", "Place", "Transition"]
