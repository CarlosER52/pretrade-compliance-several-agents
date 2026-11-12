python -c "
from src.agents.llm_client import LLMClient
from src.schemas import AnalisisContexto

client = LLMClient()
resultado = client.parse_structured(
    system_prompt='Eres un analista de compliance.',
    user_prompt='Analiza esta orden: comprar 1000 TSLA. La regla R1 falló.',
    response_model=AnalisisContexto,
)
print(resultado.model_dump_json(indent=2))
"