# EvaluAI Profesor - Documentación del Proyecto

## 🎯 Visión y Propósito

**EvaluAI Profesor** es una plataforma SaaS inteligente diseñada para profesores de educación básica, media y superior en Colombia, que automatiza la evaluación de trabajos estudiantiles con retroalimentación detallada y granular.

### Propósito Central
Eliminar la carga administrativa de la calificación manual, permitiendo a los profesores enfocarse en la enseñanza personalizada, mientras los estudiantes reciben retroalimentación constructiva, específica y oportuna.

---

## 👥 Público Objetivo

**Usuario Primario:** Profesores de educación en Colombia
- **Edad:** 25-60 años
- **Nivel:** Básica primaria, básica secundaria, media, técnica y universitaria
- **Dolor principal:** Sobrecarga de trabajo por calificación manual de 30-50 trabajos semanales
- **Necesidad:** Evaluación rápida pero manteniendo calidad y personalización

---

## 💼 Modelo de Negocio

### Plan Único: "Profesor"

| Concepto | Valor |
|----------|-------|
| **Precio mensual** | $30.000 COP |
| **Palabras incluidas** | 120.000 palabras/mes |
| **Evaluaciones** | Ilimitadas (dentro del límite de palabras) |
| **Bloque extra** | +50.000 palabras por $10.000 COP |
| **Máximo bloques extra** | 10 bloques (620.000 palabras totales) |

### Proyección Económica
- **Margen de ganancia:** ~85%
- **Costo AWS por usuario promedio:** ~$4.300 COP
- **Ganancia neta por usuario:** ~$25.700 COP

---

## ⚡ Funcionalidades Core

### 1. Multi-Asignatura
Soporta evaluación en todas las materias:
- 📐 **Matemáticas** (ejercicios, problemas, demostraciones)
- 📚 **Lengua Castellana** (ensayos, análisis literario)
- 🗣️ **Inglés** (writing, comprensión, gramática)
- 🌍 **Ciencias Sociales** (análisis histórico, ensayos)
- 🔬 **Ciencias Naturales** (informes, metodología científica)
- 🎨 **Artes, Filosofía, Educación Física** (extensible)

### 2. Evaluación Granular (NO en Bloque)
- Segmentación inteligente por tipo de contenido
- Evaluación individual de cada sección/párrafo/ejercicio
- Retroalimentación específica por segmento
- Identificación precisa de errores y aciertos

### 3. Sistema de Rúbricas Dinámicas
- Rúbricas por defecto según asignatura
- Personalización completa de criterios y pesos
- Plantillas predefinidas (ensayo, monografía, ejercicios)
- Guardado de rúbricas personalizadas

### 4. Visualización por Semáforos
- 🟢 **Verde** (8-10): Excelente
- 🟡 **Amarillo** (6-7.9): Aceptable con observaciones
- 🔴 **Rojo** (<6): Requiere revisión significativa
- Visualización por segmento y global

### 5. Control de Costos Transparente
- Estimación de costo antes de evaluar
- Contador de palabras en tiempo real
- Alertas al 75%, 90% y 100% del límite
- Compra de bloques extra sin fricción

### 6. Exportación de Reportes
- PDF con evaluación detallada
- Excel con calificaciones consolidadas
- Retroalimentación para estudiantes

---

## 🏗️ Arquitectura Técnica

### Stack Tecnológico

| Capa | Tecnología |
|------|------------|
| **Framework AI** | Agent Squad (AWS Labs) |
| **LLM** | DeepSeek-V3 (vía API) |
| **Backend** | Python 3.11 + FastAPI |
| **Frontend** | React 18 + TypeScript |
| **Base de datos** | PostgreSQL (Railway) o SQLite (local) |
| **Almacenamiento** | Volúmenes Railway o local filesystem |
| **Pagos** | PayU Colombia (PSE, tarjetas, efectivo) |
| **Hosting** | Railway ($5/mes) o local |

### Componentes Principales

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│              (React + TypeScript)                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                       BACKEND                                │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │   API       │  │  Document    │  │  Payment         │   │
│  │   Gateway   │  │  Processor   │  │  Gateway (PayU)  │   │
│  └─────────────┘  └──────────────┘  └──────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                     AGENT SQUAD                              │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │   Parser    │  │  Evaluator   │  │  Segmenter       │   │
│  │   Agent     │  │  Agent       │  │  Agent           │   │
│  └─────────────┘  └──────────────┘  └──────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                     INFRAESTRUCTURA                          │
│         AWS Bedrock | DynamoDB | S3 | Lambda                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Flujo de Usuario

### Flujo de Evaluación

```
1. LOGIN
   └── Accede con credenciales

2. CONFIGURAR RÚBRICA (Paso 1)
   ├── Selecciona asignatura
   ├── Elige plantilla o crea personalizada
   └── Define criterios y pesos

3. SUBIR DOCUMENTO (Paso 2)
   ├── Sube PDF, DOCX o TXT
   └── Sistema detecta palabras automáticamente

4. ESTIMAR COSTO (Paso 3)
   ├── Muestra: palabras totales, costo estimado
   ├── Alerta si excede presupuesto
   └── Opción de comprar bloque extra si es necesario

5. CONFIRMAR Y EVALUAR (Paso 4)
   └── Procesamiento con Agent Squad

6. VER RESULTADOS (Paso 5)
   ├── Calificación global con semáforo
   ├── Tabla de segmentos evaluados
   ├── Retroalimentación detallada por sección
   └── Opciones de exportar PDF
```

---

## 🎨 Sistema de Segmentación por Asignatura

### Matemáticas
- **Segmenta por:** Ejercicio, problema, demostración, paso de resolución
- **Criterios default:** Procedimiento (40%), Resultado (20%), Justificación (25%), Notación (15%)

### Lengua Castellana
- **Segmenta por:** Párrafo, introducción, desarrollo, conclusión
- **Criterios default:** Tesis (25%), Coherencia (25%), Cohesión (20%), Análisis (20%), Ortografía (10%)

### Inglés
- **Segmenta por:** Comprensión lectora, ensayo, gramática, diálogo
- **Criterios default:** Grammar (30%), Vocabulary (25%), Coherence (25%), Task completion (20%)

### Ciencias Sociales
- **Segmenta por:** Contexto, causas, desarrollo, consecuencias, conclusión
- **Criterios default:** Contextualización (25%), Análisis causal (25%), Fuentes (25%), Argumentación (15%), Perspectiva crítica (10%)

### Ciencias Naturales
- **Segmenta por:** Hipótesis, metodología, resultados, discusión, conclusión
- **Criterios default:** Validez científica, Metodología, Precisión de datos, Análisis, Conclusión fundamentada

---

## 💳 Integración de Pagos (Colombia)

### PayU
- **Métodos:** PSE (transferencia bancaria), tarjetas crédito/débito, efectivo (Baloto, Efecty)
- **Comisión:** ~2.99% + $900 COP por transacción
- **Integración:** SDK Python oficial

### Flujo de Pago
```
1. Usuario selecciona plan o bloque extra
2. Genera checkout en PayU
3. Usuario paga (PSE, tarjeta o efectivo)
4. Webhook confirma pago
5. Activación inmediata de servicio/crédito
```

---

## 📊 Métricas de Éxito (KPIs)

### Técnicos
- Tiempo promedio de evaluación: <30 segundos
- Precisión de segmentación: >95%
- Satisfacción de retroalimentación: >4.5/5

### Negocio
- Meta primer año: 500 profesores suscritos
- Meta ingresos mensuales: $15.000.000 COP
- Retención mensual: >80%
- Churn rate mensual: <5%

---

## 🚀 Roadmap

### Fase 1: MVP (Mes 1-2)
- [ ] Sistema de autenticación
- [ ] Evaluación de lenguaje y matemáticas básicas
- [ ] Integración PayU
- [ ] Dashboard básico

### Fase 2: Expansión (Mes 3-4)
- [ ] Agregar todas las asignaturas
- [ ] Sistema de rúbricas personalizables
- [ ] Exportación a PDF
- [ ] App móvil (responsive)

### Fase 3: Escalado (Mes 5-6)
- [ ] API pública para instituciones
- [ ] Análisis de tendencias (reportes institucionales)
- [ ] Integración con LMS (Google Classroom, Moodle)
- [ ] Versión institucional multi-usuario

---

## ⚠️ Consideraciones Importantes

### Limitaciones Técnicas
- Máximo de palabras por documento: 50.000 (por limitaciones de prompt)
- Formatos soportados: PDF, DOCX, TXT (imágenes con OCR en roadmap)
- Idiomas: Español (principal), Inglés (nativo), otros en desarrollo

### Aspectos Legales
- Política de privacidad de datos estudiantiles
- Cumplimiento de ley de protección de datos (Colombia)
- Términos de uso claros sobre propiedad intelectual
- Almacenamiento temporal de documentos (30 días default)

---

## 📞 Contacto y Soporte

**Equipo:** [Por definir]
**Email:** soporte@evaluai.com
**Documentación técnica:** Ver `agent.md`

---

*Última actualización: Marzo 2025*
*Versión: 1.0*
