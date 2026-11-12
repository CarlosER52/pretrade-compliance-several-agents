"""Script de verificación formal de la red con z3-solver.

Uso:
    python -m verification.run_verification --net src/petri/definitions.yaml
"""

import argparse
import sys
from pathlib import Path

import yaml

# Añadir la raíz del proyecto al sys.path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.petri.net import PetriNet, Place, Transition
from verification.properties import PROPERTIES


def load_net_from_yaml(path: str) -> PetriNet:
    """Carga la red desde YAML y construye un PetriNet estructural.

    Solo carga places y transiciones con sus inputs/outputs.
    Las guardas y acciones se resuelven en tiempo de ejecución,
    no en verificación estructural.
    """
    with open(path, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)

    net = PetriNet()

    for p in spec.get("places", []):
        place = Place(
            id=p["id"],
            type=p.get("type", "data"),
            capacity=p.get("capacity"),
            initial_tokens=p.get("initial_tokens", 0),
        )
        net.add_place(place)

    for t in spec.get("transitions", []):
        transition = Transition(
            id=t["id"],
            inputs=[tuple(x) for x in t.get("inputs", [])],
            outputs=[tuple(x) for x in t.get("outputs", [])],
            guard=None,  # no necesaria para verificación estructural
            action=None,
        )
        net.add_transition(transition)

    return net


def verify_all(net: PetriNet) -> int:
    """Ejecuta todas las propiedades y devuelve el número de fallos."""
    failures = 0
    for name, fn in PROPERTIES.items():
        ok, msg = fn(net)
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {name}: {msg}")
        if not ok:
            failures += 1
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--net", required=True, help="Ruta al YAML de la red")
    args = parser.parse_args()

    net = load_net_from_yaml(args.net)
    print(f"Red cargada: {len(net.places)} places, {len(net.transitions)} transitions\n")

    failures = verify_all(net)
    if failures:
        print(f"\n{failures} propiedad(es) fallaron.")
        return 1
    print("\nTodas las propiedades pasaron.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())