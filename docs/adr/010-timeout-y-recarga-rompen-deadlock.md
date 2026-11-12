# ADR-010: Timeout y recarga rompen deadlock por agotamiento de recursos

## Estado

Aceptado.

## Contexto

La verificación formal con z3-solver (`verification/run_verification.py`)
detectó que la red de Petri permitía un estado alcanzable sin transiciones
disparables. El contraejemplo más probable es:

1. Una orden llega a `p_validacion_reglas` (reglas duras ejecutadas).
2. Los 2 tokens de `p_pool_analista` están ocupados por otras órdenes.
3. Los 10 tokens de `p_api_budget` se agotaron en la ventana actual.
4. `t_ejecutar_analisis` no puede dispararse (faltan tokens de pool y budget).
5. No hay ninguna otra transición que libere esos tokens.
6. **Deadlock**: la orden queda atascada indefinidamente.

En un sistema de compliance, una orden atascada es un riesgo operacional
real: no se ejecuta, no se rechaza, no se audita. Queda en el limbo.

## Decisión

Añadir dos transiciones de tipo `timer` a la red:

1. **`t_timeout_analisis`**: si una orden lleva más de SLA esperando en
   `p_validacion_reglas` sin que el pool de analistas se libere, la orden
   se saca a `p_error` (escalado manual). No requiere token de pool, solo
   el timer.

2. **`t_recargar_budget`**: cada ventana temporal, `p_api_budget` se
   recarga a 10 tokens. Esto evita que el agotamiento del presupuesto LLM
   bloquee indefinidamente a los agentes.

El verificador Z3 trata ambas transiciones como **siempre potencialmente
habilitadas** (modelan eventos temporales que eventualmente ocurren), lo
que rompe el deadlock estructural.

## Consecuencia

- La red pasa a ser `deadlock_free` según el verificador Z3.
- La verificación formal se vuelve parte del CI (hook de pre-commit).
- El ADR documenta el hallazgo y la corrección, demostrando que la
  verificación formal no es un adorno: es lo que obligó a rediseñar la red.

## Alternativas consideradas

- **Modelar el pool de analistas como recurso infinito**: pierde la
  verificación de "no más de N analistas concurrentes". El rate limiting
  se vuelve una garantía de implementación, no de diseño. Descartada
  porque oscurece la contención.

- **No verificar `deadlock_free`**: aceptar el riesgo operacional.
  Descartada porque el sistema es safety-critical.

- **Model checking completo con nuXmv o Spin**: más potente, pero
  introduce dependencias pesadas y no es necesario para la red actual
  (17 places, 10 transiciones). El Z3 simplificado es suficiente.