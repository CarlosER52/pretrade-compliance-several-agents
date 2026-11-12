python -c "
from src.petri.transitions import ejecutar_reglas_action

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
print('fallos_total:', v['fallos_total'])
for r in v['reglas']:
    print(f\"  {r['regla_id']}: {r['resultado']} - {r['detalle']}\")
"