# EvaluAI Profesor - Configuración de Agentes AI

## 🤖 Arquitectura de Agentes

Sistema basado en **Agent Squad** con orquestación multi-nivel para evaluación académica segmentada.

```
┌─────────────────────────────────────────────────────────────┐
│                  ORQUESTADOR MAESTRO                         │
│              (AgentSquad Principal)                          │
│                                                              │
│  Responsabilidades:                                          │
│  • Router de asignaturas                                     │
│  • Gestión de sesiones de usuario                            │
│  • Control de límites de palabras                            │
│  • Coordinación entre agentes especializados                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
   ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
   │   Parser     │ │  Segmenter   │ │  Evaluator   │
   │   Agent      │ │  Agent       │ │  Agent       │
   └──────────────┘ └──────────────┘ └──────────────┘
           │               │               │
           └───────────────┼───────────────┘
                           ▼
                  ┌─────────────────┐
                  │  Report Builder │
                  │  Agent          │
                  └─────────────────┘
```

---

## 🎭 Definición de Agentes

### 1. DocumentParserAgent

**Propósito:** Extraer texto limpio de documentos subidos (PDF, DOCX, TXT).

**Configuración:**
```python
DocumentParserAgentOptions(
    name="DocumentParser",
    description="Extrae texto de archivos PDF, DOCX y TXT manteniendo estructura",
    tools=[
        "extract_pdf",
        "extract_docx", 
        "extract_txt",
        "detect_encoding"
    ]
)
```

**Salida esperada:**
```json
{
  "texto_limpio": "string",
  "metadata": {
    "total_palabras": 12500,
    "total_paginas": 15,
    "formato_original": "pdf",
    "estructura_detectada": ["titulo", "subtitulos", "parrafos"]
  }
}
```

---

### 2. SegmenterAgent

**Propósito:** Dividir el documento en segmentos evaluables según la asignatura.

**Configuración:**
```python
SegmenterAgentOptions(
    name="SegmenterAgent",
    description="Segmenta documentos según estructura propia de cada asignatura",
    asignaturas_soportadas=["matematicas", "lenguaje", "sociales", "ingles", "ciencias"]
)
```

**Comportamiento por Asignatura:**

#### Matemáticas
```python
PATRONES_MATEMATICAS = [
    (r'Ejercicio\s+(\d+)[\.:]?\s*(.+?)(?=Ejercicio\s+\d+|$)', 'ejercicio'),
    (r'Problema\s+(\d+)[\.:]?\s*(.+?)(?=Problema\s+\d+|$)', 'problema'),
    (r'Paso\s+(\d+)[\.:]?\s*(.+?)(?=Paso\s+\d+|$)', 'paso_resolucion'),
    (r'Demostración[\.:]?\s*(.+?)(?=Demostración|$)', 'demostracion'),
]

METADATA_EXTRAIDA = ["formulas_detectadas", "numeros", "variables"]
```

#### Ciencias Sociales
```python
PATRONES_SOCIALES = [
    (r'(?:Contexto histórico|Antecedentes)[\.:]?\s*(.+?)(?=Desarrollo|Consecuencias|$)', 'contexto'),
    (r'(?:Causas|Orígenes)[\.:]?\s*(.+?)(?=Consecuencias|Desarrollo|$)', 'causas'),
    (r'(?:Desarrollo|Desarrollo histórico)[\.:]?\s*(.+?)(?=Consecuencias|Conclusión|$)', 'desarrollo'),
    (r'(?:Consecuencias|Impacto|Efectos)[\.:]?\s*(.+?)(?=Conclusión|$)', 'consecuencias'),
    (r'Conclusión[\.:]?\s*(.+?)(?=$)', 'conclusion'),
]

METADATA_EXTRAIDA = ["fechas_detectadas", "nombres_propios", "lugares"]
```

#### Inglés
```python
PATRONES_INGLES = [
    (r'Reading\s+Comprehension[\.:]?\s*(.+?)(?=Questions|$)', 'comprension_lectora'),
    (r'Essay[\.:]?\s*(.+?)(?=Essay|$)', 'ensayo'),
    (r'Grammar\s+Exercise\s+(\d+)[\.:]?\s*(.+?)(?=Grammar|$)', 'gramatica'),
    (r'Dialogue[\.:]?\s*(.+?)(?=Dialogue|$)', 'dialogo'),
]

METADATA_EXTRAIDA = ["posibles_intrusiones_espanol", "tiempos_verbales_usados"]
```

**Salida esperada:**
```json
{
  "segmentos": [
    {
      "numero": 1,
      "tipo": "ejercicio",
      "contenido": "texto del segmento",
      "metadata": {
        "formulas_detectadas": ["x^2 + 2x + 1"],
        "longitud": 150
      }
    }
  ],
  "total_segmentos": 15,
  "asignatura_detectada": "matematicas"
}
```

---

### 3. EvaluatorAgent

**Propósito:** Evaluar cada segmento individualmente usando la rúbrica configurada.

**Configuración:**
```python
EvaluatorAgentOptions(
    name="EvaluatorAgent",
    description="Evalúa segmentos académicos según rúbricas personalizadas",
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    max_tokens=2000,
    temperature=0.0  # Precisión sobre creatividad
)
```

**Prompt Template por Asignatura:**

#### Prompt Matemáticas
```
Eres un profesor de matemáticas evaluando paso a paso.

SEGMENTO #{numero} - Tipo: {tipo}
Contenido del estudiante:
{contenido}

CRITERIOS DE EVALUACIÓN:
{criterios_json}

INSTRUCCIONES:
1. Evalúa cada criterio del 1 al 10
2. Verifica si el procedimiento es lógico y matemáticamente correcto
3. Identifica errores en cálculos o razonamiento
4. Muestra el desarrollo correcto si hay errores
5. Sugiere el método correcto

Responde ESTRICTAMENTE en JSON:
{
  "criterios_evaluados": [
    {"nombre": "Procedimiento", "puntuacion": X, "comentario": "..."}
  ],
  "calificacion": X.X,
  "retroalimentacion": "Explicación detallada...",
  "errores_detectados": ["error1", "error2"],
  "solucion_correcta": "Desarrollo paso a paso correcto"
}
```

#### Prompt Ciencias Sociales
```
Eres un profesor de ciencias sociales evaluando análisis histórico.

SEGMENTO #{numero} - Tipo: {tipo} ({contexto_tematico})
Contenido del estudiante:
{contenido}

CRITERIOS DE EVALUACIÓN:
{criterios_json}

INSTRUCCIONES:
1. Verifica precisión de fechas y hechos históricos
2. Evalúa si las causas/consecuencias están bien relacionadas
3. Identifica omisiones importantes
4. Valora la perspectiva crítica (¿considera múltiples voces?)
5. Señala anacronismos o falta de contexto

Responde ESTRICTAMENTE en JSON:
{
  "criterios_evaluados": [
    {"nombre": "Contextualización", "puntuacion": X, "comentario": "..."}
  ],
  "calificacion": X.X,
  "retroalimentacion": "Análisis detallado...",
  "hechos_verificados": ["hecho1: correcto", "hecho2: incorrecto - corrección"],
  "fuentes_sugeridas": ["fuente1", "fuente2"]
}
```

#### Prompt Inglés
```
You are an English teacher evaluating student work.

SEGMENT #{numero} - Type: {tipo}
Student content:
{contenido}

EVALUATION CRITERIA:
{criterios_json}

INSTRUCTIONS:
1. Identify grammar errors (specify the rule broken)
2. Suggest better vocabulary choices
3. Check if the style is appropriate for the task
4. Evaluate organization and flow
5. Provide the corrected version

Respond STRICTLY in JSON:
{
  "criterios_evaluados": [
    {"nombre": "Grammar", "puntuacion": X, "comentario": "..."}
  ],
  "calificacion": X.X,
  "retroalimentacion": "Detailed feedback...",
  "errores_gramaticales": ["error1 -> correction"],
  "version_corregida": "Complete corrected text"
}
```

#### Prompt Lenguaje
```
Eres un profesor de lengua castellana evaluando producción textual.

SEGMENTO #{numero} - Tipo: {tipo}
Contenido del estudiante:
{contenido}

CRITERIOS DE EVALUACIÓN:
{criterios_json}

INSTRUCCIONES:
1. Identifica problemas de coherencia (saltos lógicos)
2. Señala errores de cohesión (falta de conectores)
3. Evalúa la profundidad del análisis literario
4. Corrige errores ortográficos y de puntuación
5. Sugiere cómo reescribir frases confusas

Responde ESTRICTAMENTE en JSON:
{
  "criterios_evaluados": [
    {"nombre": "Tesis", "puntuacion": X, "comentario": "..."}
  ],
  "calificacion": X.X,
  "retroalimentacion": "Retroalimentación constructiva...",
  "errores_ortograficos": ["error -> corrección"],
  "sugerencias_mejora": ["sugerencia1", "sugerencia2"]
}
```

**Salida esperada:**
```json
{
  "segmento_id": 1,
  "calificacion": 7.5,
  "criterios_detallados": [...],
  "retroalimentacion": "texto completo",
  "version_corregida": "texto mejorado",
  "tokens_consumidos": {"input": 1500, "output": 800}
}
```

---

### 4. ReportBuilderAgent

**Propósito:** Consolidar todas las evaluaciones de segmentos en un reporte final coherente.

**Configuración:**
```python
ReportBuilderAgentOptions(
    name="ReportBuilderAgent",
    description="Genera reportes consolidados con semáforos y análisis global",
    template_formats=["json", "pdf", "html"]
)
```

**Funciones:**
- Calcular calificación global ponderada
- Generar resumen ejecutivo
- Identificar patrones de error
- Sugerir plan de mejora
- Crear visualizaciones (semáforos, gráficos)

**Salida esperada:**
```json
{
  "reporte": {
    "calificacion_global": 7.8,
    "semaforo_global": "AMARILLO",
    "total_segmentos": 15,
    "distribucion_semaforos": {
      "verde": 8,
      "amarillo": 5,
      "rojo": 2
    },
    "segmentos_criticos": [3, 12],
    "fortalezas": ["Buena argumentación", "Vocabulario rico"],
    "areas_mejora": ["Cohesión textual", "Precisión de datos"],
    "recomendacion_general": "Texto personalizado según desempeño"
  }
}
```

---

## 🔄 Flujo de Trabajo (Workflow)

### Diagrama de Secuencia

```
Usuario          Orquestador       Parser      Segmenter     Evaluator     Report
  │                  │               │            │             │            │
  │──Sube doc───────▶│               │            │             │            │
  │                  │──Extraer─────▶│            │             │            │
  │                  │◀──Texto───────│            │             │            │
  │                  │               │            │             │            │
  │                  │──Segmentar─────────────────▶│             │            │
  │                  │◀──Segmentos─────────────────│             │            │
  │                  │               │            │             │            │
  │                  │──Evaluar seg1────────────────────────────▶│            │
  │                  │──Evaluar seg2────────────────────────────▶│            │
  │                  │──Evaluar segN────────────────────────────▶│            │
  │                  │◀──Resultados evaluación───────────────────│            │
  │                  │               │            │             │            │
  │                  │──Consolidar───────────────────────────────────────────▶│
  │                  │◀──Reporte final────────────────────────────────────────│
  │◀──Resultado──────│               │            │             │            │
```

### Pseudocódigo del Flujo

```python
async def evaluar_documento_completo(archivo, asignatura, rubrica, user_id):
    # 1. Verificar límites de palabras
    palabras = contar_palabras(archivo)
    if not usuario.puede_evaluar(palabras):
        return {"error": "Límite excedido", "comprar_bloque": True}
    
    # 2. Parsear documento
    texto = await DocumentParserAgent.process(archivo)
    
    # 3. Segmentar según asignatura
    segmentos = await SegmenterAgent.process(texto, asignatura)
    
    # 4. Evaluar cada segmento (PARALELO)
    evaluaciones = await asyncio.gather(*[
        EvaluatorAgent.process(seg, rubrica, asignatura) 
        for seg in segmentos
    ])
    
    # 5. Construir reporte final
    reporte = await ReportBuilderAgent.consolidar(evaluaciones, rubrica)
    
    # 6. Descontar palabras usadas
    await usuario.consumir_palabras(palabras)
    
    return reporte
```

---

## 📊 Cálculo de Costos por Evaluación

### Fórmula de Estimación

```python
def estimar_costo_evaluacion(palabras_documento, num_segmentos, asignatura):
    """
    palabras_documento: total de palabras del archivo
    num_segmentos: cantidad de segmentos detectados
    asignatura: tipo de asignatura (afecta complejidad del prompt)
    """
    
    # Tokens de entrada (documento + prompts + rúbrica)
    tokens_input = (palabras_documento / 0.75) + (num_segmentos * 500)
    
    # Tokens de salida (retroalimentación por segmento)
    tokens_output = num_segmentos * 400  # ~400 tokens por segmento
    
    # Costos AWS Bedrock (Claude 3.5 Sonnet)
    costo_input = (tokens_input / 1_000_000) * 3.0   # $3 por millón de tokens
    costo_output = (tokens_output / 1_000_000) * 15.0  # $15 por millón
    
    costo_total_usd = costo_input + costo_output
    costo_total_cop = costo_total_usd * 4100  # Tasa aproximada
    
    return {
        "tokens_input": int(tokens_input),
        "tokens_output": int(tokens_output),
        "costo_usd": round(costo_total_usd, 4),
        "costo_cop": round(costo_total_cop, 2),
        "costo_por_segmento_usd": round(costo_total_usd / num_segmentos, 4)
    }
```

### Ejemplos de Estimación

| Escenario | Palabras | Segmentos | Costo COP | Segmentos |
|-----------|----------|-----------|-----------|-----------|
| Ensayo corto (Lengua) | 1,500 | 5 | ~$180 | 5 párrafos |
| Taller matemático | 800 | 12 ejercicios | ~$220 | 12 problemas |
| Monografía sociales | 8,000 | 8 secciones | ~$650 | 8 secciones |
| Examen inglés | 2,000 | 10 partes | ~$280 | 10 ejercicios |

---

## ⚙️ Configuración de Infraestructura

### Variables de Entorno

```bash
# AWS
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=xxxxx
AWS_SECRET_ACCESS_KEY=xxxxx
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# Base de datos
DYNAMODB_TABLE_USERS=evaluai_users
DYNAMODB_TABLE_EVALUATIONS=evaluai_evaluations
DYNAMODB_TABLE_RUBRICS=evaluai_rubrics

# Almacenamiento
S3_BUCKET=evaluai-documents
S3_EXPIRATION_DAYS=30

# Pagos (PayU)
PAYU_API_KEY=xxxxx
PAYU_API_LOGIN=xxxxx
PAYU_MERCHANT_ID=xxxxx
PAYU_ACCOUNT_ID=xxxxx
PAYU_URL=https://sandbox.checkout.payulatam.com/...

# Límites
DEFAULT_WORD_LIMIT=120000
EXTRA_BLOCK_WORDS=50000
EXTRA_BLOCK_PRICE=10000
MAX_EXTRA_BLOCKS=10

# API
API_RATE_LIMIT=100  # requests per minute
API_TIMEOUT=30      # seconds
```

---

## 🔒 Consideraciones de Seguridad

1. **Validación de archivos:** Solo PDF, DOCX, TXT. Tamaño máximo: 10MB
2. **Sanitización de inputs:** Limpiar texto antes de enviar a LLM
3. **Rate limiting:** Máximo 10 evaluaciones por minuto por usuario
4. **Encriptación:** En tránsito (TLS) y en reposo (S3/DynamoDB)
5. **Anonimización:** No almacenar nombres de estudiantes, solo IDs

---

## 📚 Dependencias

```txt
# Core
agent-squad[aws]==0.1.0
boto3>=1.28.0
botocore>=1.31.0

# API
fastapi==0.104.0
uvicorn[standard]==0.24.0
pydantic==2.5.0

# Procesamiento de documentos
PyPDF2==3.0.1
python-docx==1.1.0

# Utilidades
python-multipart==0.0.6
aiofiles==23.2.0

# Testing
pytest==7.4.0
pytest-asyncio==0.21.0
```

---

## 🧪 Testing de Agentes

### Test Unitario: EvaluatorAgent

```python
import pytest

@pytest.mark.asyncio
async def test_evaluador_matematicas():
    agent = EvaluatorAgent(asignatura="matematicas")
    
    segmento = {
        "numero": 1,
        "tipo": "ejercicio",
        "contenido": "Resolver: x^2 + 5x + 6 = 0"
    }
    
    rubrica = {
        "criterios": [
            {"nombre": "Procedimiento", "peso": 0.4},
            {"nombre": "Resultado", "peso": 0.3},
            {"nombre": "Justificación", "peso": 0.3}
        ]
    }
    
    resultado = await agent.evaluar(segmento, rubrica)
    
    assert "calificacion" in resultado
    assert 0 <= resultado["calificacion"] <= 10
    assert "retroalimentacion" in resultado
    assert "criterios_evaluados" in resultado
```

---

## 📝 Notas de Implementación

1. **Optimización de costos:** Implementar caché de rúbricas para no enviarlas completas en cada llamada
2. **Manejo de errores:** Si un segmento falla, continuar con los demás y marcar error
3. **Lenguajes:** Prompts en español para lenguaje/sociales/matemáticas, inglés para inglés
4. **Timeout:** Máximo 5 segundos por segmento, máximo 60 segundos por documento completo

---

*Documento técnico para desarrolladores*
*Última actualización: Marzo 2025*
