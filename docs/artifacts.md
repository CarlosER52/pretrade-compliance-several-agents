# Artefactos del flujo de compliance

Durante la validación de una orden, el sistema produce varios artefactos
JSON que documentan cada paso. Estos artefactos son **contratos inmutables**
(ADR-005): una vez producidos, no se modifican, y el siguiente paso los
consume.

## 1. `orden.json` (input)

La orden propuesta por el cliente o la mesa. Ejemplo:

```json
{
  "orden_id": "ORD-2026-11-00001",
  "instrumento": "stocks",
  "tipo": "buy",
  "cantidad": 1000,
  "simbolo": "TSLA",
  "precio": 200,
  "tipo_orden": "limit",
  "cuenta_id": "ACC-4471",
  "cliente_id": "CLI-001",
  "sector": "tech"
}