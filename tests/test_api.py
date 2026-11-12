import os
import json
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError
from typing import Literal

# 1. Definir el modelo Pydantic (el mismo que usas en tu proyecto)
class AnalisisContexto(BaseModel):
    cliente_en_watchlist: bool
    patron_inusual: bool
    conflicto_politica: bool
    justificacion: str = Field(min_length=20)
    confianza: float = Field(ge=0.0, le=1.0)

# 2. Configurar el cliente compatible con OpenAI
client = OpenAI(
    api_key=os.getenv("ZAI_API_KEY"),  # Asegúrate de tener esta variable de entorno
    base_url="https://api.z.ai/api/paas/v4/"
)

# 3. Prompt del sistema que obliga al modelo a devolver el JSON correcto
system_prompt = """
Eres un analista de compliance. Debes devolver ÚNICAMENTE un objeto JSON que se ajuste a este esquema exacto:
{
  "cliente_en_watchlist": true/false,
  "patron_inusual": true/false,
  "conflicto_politica": true/false,
  "justificacion": "string con al menos 20 caracteres",
  "confianza": 0.0 a 1.0
}
No incluyas markdown, ni texto adicional, solo el JSON.
"""

# 4. Datos de prueba (simulando tu contexto)
user_prompt = """
Analiza el contexto de esta orden:
- Orden: Comprar 1000 acciones de TSLA a 200.
- Regla dura R1_posicion: FAIL (Posición 13.33% > 10%).
- Cliente: No está en watchlist, pero la orden es 3x su promedio.
"""

try:
    # 5. Llamada a la API usando el modo json_object
    response = client.chat.completions.create(
        model="glm-4.7-flash",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"}, # Z.ai solo soporta esto
        temperature=0.1, # Baja temperatura para mayor consistencia
    )

    # 6. Extraer y validar el JSON
    raw_content = response.choices[0].message.content
    print("Respuesta cruda del modelo:")
    print(raw_content)

    # Parsear el string JSON a un diccionario
    data = json.loads(raw_content)

    # Validar con Pydantic
    analisis = AnalisisContexto(**data)
    print("\n✅ Validación Pydantic exitosa:")
    print(analisis.model_dump_json(indent=2))

except json.JSONDecodeError as e:
    print(f"❌ Error: El modelo no devolvió un JSON válido. {e}")
except ValidationError as e:
    print(f"❌ Error: El JSON no cumple con el esquema de Pydantic. {e}")
except Exception as e:
    print(f"❌ Error inesperado: {e}")