"""Guarda crítica: piso de reglas duras.

Si hay fallos en reglas duras, el riesgo resultante DEBE ser >= HIGH.
El agente nunca puede bajar el riesgo por debajo del piso.
"""


def validar_piso(context: dict, places: dict):
    """Evalúa la guarda de piso sobre el contexto de la transición.

    `context` debe contener las claves `validacion`, `analisis` y
    `clasificacion` (objetos Pydantic o dicts compatibles).
    """
    validacion = context.get("validacion")
    analisis = context.get("analisis")
    clasificacion = context.get("clasificacion")

    if validacion is None or analisis is None or clasificacion is None:
        return False, "contexto_incompleto"

    # Piso de reglas duras
    if validacion["fallos_total"] > 0:
        if clasificacion["riesgo"] in ("LOW", "MEDIUM"):
            return False, "VIOLACIÓN: agente intentó bajar riesgo con fallos"
        clasificacion["piso_aplicado"] = True

    # Coherencia con watchlist
    if analisis["cliente_en_watchlist"] and clasificacion["riesgo"] == "LOW":
        return False, "VIOLACIÓN: watchlist no puede ser LOW"

    # Hash de inputs
    if clasificacion["hash_inputs"] != validacion["hash_inputs"]:
        return False, "VIOLACIÓN: hash no coincide"

    return True, "OK"
