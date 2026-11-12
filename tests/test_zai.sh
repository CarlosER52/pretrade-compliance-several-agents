python -c "
from src.petri.transitions import ejecutar_reglas_action, clasificar_con_piso_action
from src.agents.analyst import analyst_agent_action

orden = {'orden_id': 'ORD-2026-11-00001', 'instrumento': 'stocks', 'tipo': 'buy',
         'cantidad': 1000, 'simbolo': 'TSLA', 'precio': 200,
         'cuenta_id': 'ACC-4471', 'cliente_id': 'CLI-001', 'sector': 'tech'}
contexto = {'capital_cuenta': 1500000, 'posicion_actual': {'TSLA': 0}}

v = ejecutar_reglas_action({'orden': orden, 'contexto_cliente': contexto}, {})
print('fallos_total:', v['fallos_total'])

analisis = analyst_agent_action({'orden': orden, 'validacion': v, 'contexto_cliente': contexto}, {})
print('justificacion:', analisis['justificacion'][:80], '...')
print('confianza:', analisis['confianza'])

c = clasificar_con_piso_action({'validacion': v, 'analisis': analisis,
                                 'riesgo_sugerido_por_agente': 'LOW'}, {})
print(f\"Riesgo final: {c['riesgo']} | Piso aplicado: {c['piso_aplicado']}\")
"