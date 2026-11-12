python -c "
from src.agents.analyst import AnalystAgent
from src.schemas import ValidacionReglas, ReglaResultado

agente = AnalystAgent.__new__(AnalystAgent)
v = ValidacionReglas(
    orden_id='ORD-2026-11-00001', instrumento='stocks',
    reglas=[ReglaResultado(regla_id='R1_posicion', resultado='fail', detalle='x')],
    fallos_total=1, hash_inputs='abc',
)
orden = {'orden_id': 'ORD-2026-11-00001', 'instrumento': 'stocks', 'tipo': 'buy',
         'cantidad': 1000, 'simbolo': 'TSLA', 'precio': 200,
         'cuenta_id': 'ACC-4471', 'cliente_id': 'CLI-001', 'sector': 'tech'}
prompt = agente._build_user_prompt(orden, v, {'capital_cuenta': 1500000})
print(prompt)
print('---')
print(f'Longitud total: {len(prompt)} caracteres')
"