# 🧠 Configuración DeepSeek para EvaluAI

## ¿Por qué DeepSeek?

- **Costo:** 20x más barato que OpenAI
- **Calidad:** Excelente para español académico
- **Velocidad:** Buena latencia para evaluaciones
- **JSON Mode:** Perfecto para evaluaciones estructuradas

## Precios (Actualizados)

| Tipo | Precio | Comparación |
|------|--------|-------------|
| Input | $0.50 / 1M tokens | OpenAI GPT-4: $30 (60x más caro) |
| Output | $2.00 / 1M tokens | OpenAI GPT-4: $60 (30x más caro) |

## Costo por evaluación típica

- Documento de 3,000 palabras: ~$0.015 USD (~$60 COP)
- Con tu plan de $30,000: margen de **99.8%**

## Configuración

### 1. Obtener API Key

1. Ir a https://platform.deepseek.com
2. Crear cuenta
3. Generar API Key
4. Agregar saldo (mínimo $5 USD)

### 2. Configurar .env

```bash
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
```

### 3. Uso en código

```python
from agents import DeepSeekAgent, DeepSeekAgentOptions

agent = DeepSeekAgent(DeepSeekAgentOptions(
    name="MathEvaluator",
    description="Evalúa matemáticas",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    model="deepseek-chat"
))
```

## Modelos disponibles

- `deepseek-chat`: Versión general (recomendado)
- `deepseek-coder`: Para código/matemáticas complejas

## Monitoreo de costos

El agente incluye tracking automático:
```python
cost = agent.get_cost_estimate(input_tokens=1000, output_tokens=500)
# {'usd': 0.0015, 'cop': 6.15}
```
