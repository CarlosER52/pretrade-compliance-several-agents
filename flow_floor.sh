python -c "
from src.petri.transitions import ejecutar_reglas_action, clasificar_con_piso_action

orden = {
    'orden_id': 'ORD-2026-11-00001',
    'instrumento': 'stocks',
    'tipo': 'buy',
    'cantidad': 1000,
    'simbolo': 'TSLA',
    'precio': 200,
    'cuenta_id': 'ACC-4471',
    'cliente_id': 'CLI-001',
    'sector': 'tech',
}
contexto = {
    'capital_cuenta': 1500000,
    'posicion_actual': {'TSLA': 0},
    'exposicion_sector': {'tech': 0},
    'precio_referencia': {'TSLA': 200},
    'contra_partida_cliente_id': None,
}
v = ejecutar_reglas_action({'orden': orden, 'contexto_cliente': contexto}, {})
c = clasificar_con_piso_action({
    'validacion': v,
    'analisis': {'cliente_en_watchlist': False, 'hash_inputs': v['hash_inputs']},
    'riesgo_sugerido_por_agente': 'LOW',
}, {})
print('riesgo final:', c['riesgo'])
print('piso aplicado:', c['piso_aplicado'])
"