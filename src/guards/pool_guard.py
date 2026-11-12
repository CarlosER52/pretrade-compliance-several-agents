"""Guarda de recursos: verifica tokens de pool."""


def validar_pool(context: dict, places: dict):
    """Verifica que el pool referenciado en context tiene tokens."""
    pool_id = context.get("pool_id")
    if not pool_id:
        return False, "pool_id_ausente"
    place = places.get(pool_id)
    if place is None:
        return False, f"pool_desconocido:{pool_id}"
    requeridos = context.get("requeridos", 1)
    if len(place.tokens) < requeridos:
        return False, f"pool_sin_tokens:{pool_id}"
    return True, "OK"
