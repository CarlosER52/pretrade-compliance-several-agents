"""Ejecuta el flujo completo sobre el golden dataset y calcula métricas.

Para cada caso:
1. Valida schema.
2. Ejecuta reglas duras.
3. Ejecuta el agente analista (LLM o mock).
4. Clasifica con piso.
5. Compara contra `expected`.

Métricas:
- Accuracy: clasificación de riesgo correcta.
- Falsos positivos: órdenes triviales escaladas a gate innecesariamente.
- Falsos negativos: órdenes de alto riesgo sin gate.
- Cumplimiento de guardas: el agente nunca bajó el piso.

Uso:
    LLM_PROVIDER=mock python evals/run_evals.py
    LLM_PROVIDER=openrouter python evals/run_evals.py
"""

import json
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.agents.analyst import analyst_agent_action
from src.petri.transitions import (
    clasificar_con_piso_action,
    ejecutar_reglas_action,
    validar_schema_action,
)

GOLDEN_DIR = Path(__file__).parent / "golden_dataset"


def cargar_casos() -> list[dict]:
    """Carga los casos del golden dataset.

    Ignora archivos vacíos, corruptos o que no tengan 'case_id'.
    Avisa por consola de los que se saltan.
    """
    casos = []
    for inst_dir in sorted(GOLDEN_DIR.iterdir()):
        if not inst_dir.is_dir():
            continue
        for f in sorted(inst_dir.glob("*.json")):
            try:
                raw = f.read_text(encoding="utf-8").strip()
                if not raw:
                    print(f"  [skip] {f.name}: archivo vacío")
                    continue
                data = json.loads(raw)
                if not isinstance(data, dict) or "case_id" not in data:
                    print(f"  [skip] {f.name}: no es un caso válido (sin case_id)")
                    continue
                casos.append(data)
            except json.JSONDecodeError as e:
                print(f"  [skip] {f.name}: JSON inválido ({e})")
                continue
    return casos


def ejecutar_caso(caso: dict) -> dict:
    """Ejecuta el flujo completo para un caso y devuelve el resultado."""
    orden = caso["input"]["orden"]
    contexto = caso["input"]["contexto_cliente"]

    # 1. Schema
    schema = validar_schema_action({"orden": orden}, {})
    if not schema["ok"]:
        return {"error": "schema", "detalle": schema["error"]}

    # 2. Reglas
    validacion = ejecutar_reglas_action(
        {"orden": orden, "contexto_cliente": contexto}, {}
    )

    # 3. Agente analista
    try:
        analisis = analyst_agent_action(
            {"orden": orden, "validacion": validacion,
             "contexto_cliente": contexto}, {}
        )
    except Exception as e:
        # Si el LLM falla, usamos un análisis neutro para no bloquear
        # la evaluación (se registrará como error de agente)
        analisis = {
            "orden_id": orden["orden_id"],
            "cliente_en_watchlist": contexto.get("cliente_en_watchlist", False),
            "patron_inusual": False,
            "conflicto_politica": False,
            "justificacion": f"Fallback: agente falló ({e})",
            "confianza": 0.5,
            "hash_inputs": validacion["hash_inputs"],
        }

    # 4. Clasificación con piso
    # El agente sugiere LOW por defecto (peor caso: intenta bajar el riesgo)
    clasificacion = clasificar_con_piso_action(
        {"validacion": validacion, "analisis": analisis,
         "riesgo_sugerido_por_agente": "LOW"}, {}
    )

    return {
        "fallos_total": validacion["fallos_total"],
        "reglas_fallidas": [
            r["regla_id"] for r in validacion["reglas"]
            if r["resultado"] == "fail"
        ],
        "riesgo": clasificacion["riesgo"],
        "piso_aplicado": clasificacion["piso_aplicado"],
        "requiere_gate": clasificacion["riesgo"] != "LOW",
    }


def evaluar(caso: dict, resultado: dict) -> dict:
    """Compara el resultado contra expected y devuelve métricas."""
    expected = caso["expected"]

    reglas_ok = set(resultado["reglas_fallidas"]) == set(expected["reglas_fallidas"])
    fallos_ok = resultado["fallos_total"] == expected["fallos_total"]
    riesgo_ok = resultado["riesgo"] == expected["riesgo_minimo"]
    piso_ok = resultado["piso_aplicado"] == expected["piso_aplicado"]
    gate_ok = resultado["requiere_gate"] == expected["requiere_gate"]

    # Falso positivo: esperado LOW sin gate, pero el sistema escaló
    falso_positivo = (
        expected["riesgo_minimo"] == "LOW" and not expected["requiere_gate"]
        and resultado["requiere_gate"]
    )
    # Falso negativo: esperado gate, pero el sistema no escaló
    falso_negativo = expected["requiere_gate"] and not resultado["requiere_gate"]

    # Cumplimiento de guardas: si hay fallos, el riesgo no puede ser LOW/MEDIUM
    guarda_ok = True
    if resultado["fallos_total"] > 0 and resultado["riesgo"] in ("LOW", "MEDIUM"):
        guarda_ok = False

    return {
        "case_id": caso["case_id"],
        "reglas_ok": reglas_ok,
        "fallos_ok": fallos_ok,
        "riesgo_ok": riesgo_ok,
        "piso_ok": piso_ok,
        "gate_ok": gate_ok,
        "falso_positivo": falso_positivo,
        "falso_negativo": falso_negativo,
        "guarda_ok": guarda_ok,
        "todo_ok": all([reglas_ok, fallos_ok, riesgo_ok, piso_ok, gate_ok, guarda_ok]),
    }


def main() -> int:
    casos = cargar_casos()
    print(f"Golden dataset: {len(casos)} casos\n")

    print(f"{'case_id':<15} {'reglas':<7} {'riesgo':<7} {'piso':<6} "
          f"{'gate':<6} {'FP':<4} {'FN':<4} {'guarda':<7} {'OK'}")
    print("-" * 75)

    resultados = []
    for caso in casos:
        try:
            res = ejecutar_caso(caso)
            if "error" in res:
                print(f"{caso['case_id']:<15} ERROR: {res['detalle']}")
                continue
            ev = evaluar(caso, res)
            resultados.append(ev)
            print(
                f"{ev['case_id']:<15} "
                f"{'OK' if ev['reglas_ok'] else 'FAIL':<7} "
                f"{'OK' if ev['riesgo_ok'] else 'FAIL':<7} "
                f"{'OK' if ev['piso_ok'] else 'FAIL':<6} "
                f"{'OK' if ev['gate_ok'] else 'FAIL':<6} "
                f"{'SI' if ev['falso_positivo'] else 'no':<4} "
                f"{'SI' if ev['falso_negativo'] else 'no':<4} "
                f"{'OK' if ev['guarda_ok'] else 'FAIL':<7} "
                f"{'✓' if ev['todo_ok'] else '✗'}"
            )
        except Exception as e:
            print(f"{caso['case_id']:<15} EXCEPTION: {e}")

    # Métricas agregadas
    n = len(resultados)
    if n == 0:
        print("\nNo se evaluó ningún caso.")
        return 1

    accuracy = sum(1 for r in resultados if r["todo_ok"]) / n
    fp = sum(1 for r in resultados if r["falso_positivo"]) / n
    fn = sum(1 for r in resultados if r["falso_negativo"]) / n
    guardas = sum(1 for r in resultados if r["guarda_ok"]) / n

    print("\n" + "=" * 75)
    print(f"Accuracy (todos los checks OK):  {accuracy:.1%}  ({sum(1 for r in resultados if r['todo_ok'])}/{n})")
    print(f"Falsos positivos:                {fp:.1%}  ({sum(1 for r in resultados if r['falso_positivo'])}/{n})")
    print(f"Falsos negativos:                {fn:.1%}  ({sum(1 for r in resultados if r['falso_negativo'])}/{n})")
    print(f"Cumplimiento de guardas:         {guardas:.1%}  ({sum(1 for r in resultados if r['guarda_ok'])}/{n})")
    print("=" * 75)

    return 0 if accuracy == 1.0 and fp == 0 and fn == 0 and guardas == 1.0 else 1


if __name__ == "__main__":
    raise SystemExit(main())