LLM_PROVIDER=openrouter python -c "
from src.agents.writer import writer_agent_action

resultado = writer_agent_action({
    'orden': {'orden_id': 'ORD-2026-11-00001', 'instrumento': 'stocks',
              'tipo': 'buy', 'cantidad': 1000, 'simbolo': 'TSLA',
              'precio': 200, 'cuenta_id': 'ACC-4471',
              'cliente_id': 'CLI-001', 'sector': 'tech'},
    'validacion': {'orden_id': 'ORD-2026-11-00001', 'instrumento': 'stocks',
                   'reglas': [{'regla_id': 'R1_posicion', 'resultado': 'fail',
                               'detalle': 'Posición 13.33% > 10%'}],
                   'fallos_total': 1, 'hash_inputs': 'abc'},
    'analisis': {'orden_id': 'ORD-2026-11-00001', 'cliente_en_watchlist': False,
                 'patron_inusual': True, 'conflicto_politica': True,
                 'justificacion': 'Orden 3x mayor que el promedio.',
                 'confianza': 0.9, 'hash_inputs': 'abc'},
    'clasificacion': {'orden_id': 'ORD-2026-11-00001', 'riesgo': 'HIGH',
                      'justificacion': 'Piso aplicado por R1.',
                      'piso_aplicado': True, 'hash_inputs': 'abc'},
}, {})
print(resultado['memo'][:300])
"