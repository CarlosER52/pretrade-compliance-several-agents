# pip install zai-sdk
from zai import ZaiClient

client = ZaiClient(api_key="a5be0ae5916849af95860ef8313869ff.MoP8csyEAObcutje")

response = client.chat.completions.create(
    model="glm-4.7-flash",   # modelo gratuito
    messages=[{"role": "user", "content": "Hola, preséntate"}]
)
print(response.choices[0].message.content)