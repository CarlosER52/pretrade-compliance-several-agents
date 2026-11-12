POOLS = {
    "p_pool_analista": 2,       # 2 agentes LLM analistas concurrentes
    "p_pool_clasificador": 1,   # 1 script determinista (serial)
    "p_pool_redactor": 1,       # 1 agente LLM redactor
    "p_gate_disponible": 1,     # 1 oficial de compliance
    "p_api_budget": 10,         # 10 llamadas LLM por ventana
}

def get_pool_size(pool_id: str) -> int:
    """Devuelve el tamaño inicial de un pool, o 0 si no existe."""
    return POOLS.get(pool_id, 0)


def list_pools() -> dict:
    """Devuelve una copia del mapa de pools."""
    return dict(POOLS)