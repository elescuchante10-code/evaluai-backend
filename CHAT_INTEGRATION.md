# 💬 Integración del Chat con Agente IA

## 🎯 Propósito

El agente actúa como **guía interactivo** estilo ChatGPT dentro del dashboard, ayudando al profesor en cada paso del proceso de evaluación.

---

## 🔌 Endpoint Principal

```http
POST /agente/chat
Authorization: Bearer <token>
Content-Type: application/json
```

### Request

```json
{
  "mensaje": "Quiero evaluar un trabajo de matemáticas",
  "contexto": {
    "asignatura": "matematicas",
    "documento_id": "uuid-del-documento",
    "evaluacion_id": "uuid-de-evaluacion"
  },
  "historial": [
    {"role": "user", "content": "Hola"},
    {"role": "assistant", "content": "¡Hola! ¿En qué puedo ayudarte?"}
  ]
}
```

### Response

```json
{
  "success": true,
  "respuesta": "¡Perfecto! Para evaluar matemáticas, primero necesito que subas el documento. También puedo ayudarte a configurar una rúbrica personalizada. ¿Qué tipo de trabajo es? (ejercicios, problemas, demostraciones)",
  "accion": "evaluar",
  "data": {
    "criterios_sugeridos": [...]
  }
}
```

---

## 🎭 Acciones del Agente

El campo `accion` indica qué debe hacer el frontend:

| Acción | Significado | Acción del Frontend |
|--------|-------------|---------------------|
| `evaluar` | El usuario quiere evaluar | Abrir modal de subida de archivo o mostrar panel de evaluación |
| `rubrica` | El usuario configura rúbrica | Abrir modal/configurador de rúbricas |
| `info` | Pregunta general | Mostrar respuesta en chat |
| `general` | Conversación casual | Mostrar respuesta en chat |

---

## 🔄 Flujos de Conversación

### Flujo 1: Evaluación Guiada

```
Usuario: "Quiero evaluar un trabajo"
  ↓
Agente: "¡Claro! ¿De qué asignatura se trata?"
  ↓
Usuario: "Matemáticas"
  ↓
Agente: "Perfecto. ¿Tienes una rúbrica configurada o quieres que sugiera una?"
         [accion: "rubrica"]
  ↓
Usuario: "Sugiere una"
  ↓
Agente: "Te sugiero estos criterios: Procedimiento (40%), Resultado (30%)..."
         [data.criterios_sugeridos: [...]]
  ↓
Usuario: "Me parece bien"
  ↓
Agente: "¡Excelente! Ahora sube el documento y lo evaluamos."
         [accion: "evaluar"]
  ↓
[FRONTEND: Abre uploader de archivos]
  ↓
Usuario sube archivo → /documentos/subir
  ↓
[FRONTEND: Muestra estimación]
  ↓
Usuario: "Evaluar"
  ↓
[FRONTEND: Llama /evaluaciones/procesar]
  ↓
[FRONTEND: Muestra resultados]
  ↓
Agente: "¡Listo! El estudiante obtuvo 8.5/10. ¿Quieres que analice los resultados?"
```

### Flujo 2: Interpretar Resultados

```
Usuario: "¿Qué significa que tenga rojo en el segmento 3?"
  ↓
[FRONTEND: Envía contexto con evaluacion_id]
  ↓
Agente: "El segmento 3 tuvo calificación 4.2/10 porque el procedimiento..."
         [accion: "info"]
  ↓
Usuario: "¿Cómo puedo ayudar al estudiante a mejorar?"
  ↓
Agente: "Te sugiero practicar estos ejercicios similares..."
```

### Flujo 3: Configurar Rúbrica

```
Usuario: "Configura una rúbrica para ensayos de literatura"
  ↓
Agente: "Te propongo estos criterios: Tesis (25%), Coherencia (25%)..."
         [accion: "rubrica"]
         [data.criterios_sugeridos: [...]]
  ↓
[FRONTEND: Muestra rúbrica sugerida con opción de editar]
  ↓
Usuario: "Cambia Coherencia a 30%"
  ↓
Agente: "He ajustado los pesos. Tesis (20%), Coherencia (30%)..."
         [accion: "rubrica"]
  ↓
[FRONTEND: Actualiza vista de rúbrica]
```

---

## 💻 Implementación en React

### Estado del Chat

```javascript
const [chatState, setChatState] = useState({
  messages: [],
  contexto: {
    asignatura: null,
    documento_id: null,
    evaluacion_id: null
  },
  isLoading: false
});
```

### Función para Enviar Mensaje

```javascript
const sendMessage = async (mensaje) => {
  // Agregar mensaje del usuario
  const newMessages = [
    ...chatState.messages,
    { role: 'user', content: mensaje }
  ];
  
  setChatState(prev => ({ ...prev, messages: newMessages, isLoading: true }));
  
  try {
    const response = await fetch(`${API_URL}/agente/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        mensaje,
        contexto: chatState.contexto,
        historial: chatState.messages.slice(-10) // Últimos 10 mensajes
      })
    });
    
    const data = await response.json();
    
    // Agregar respuesta del agente
    setChatState(prev => ({
      ...prev,
      messages: [...newMessages, { 
        role: 'assistant', 
        content: data.respuesta 
      }],
      isLoading: false
    }));
    
    // Ejecutar acción si existe
    handleAgentAction(data.accion, data.data);
    
  } catch (error) {
    console.error('Error:', error);
    setChatState(prev => ({ ...prev, isLoading: false }));
  }
};
```

### Manejador de Acciones

```javascript
const handleAgentAction = (accion, data) => {
  switch (accion) {
    case 'evaluar':
      // Abrir modal de subida de archivo
      setShowUploadModal(true);
      break;
      
    case 'rubrica':
      // Abrir configurador de rúbrica
      setShowRubricModal(true);
      if (data?.criterios_sugeridos) {
        setSuggestedRubric(data.criterios_sugeridos);
      }
      break;
      
    case 'info':
    case 'general':
    default:
      // Solo mostrar mensaje, no hay acción especial
      break;
  }
};
```

### Actualizar Contexto

```javascript
// Cuando el usuario selecciona asignatura
const selectAsignatura = (asignatura) => {
  setChatState(prev => ({
    ...prev,
    contexto: { ...prev.contexto, asignatura }
  }));
};

// Cuando se sube un documento
const onDocumentUpload = (documentoId) => {
  setChatState(prev => ({
    ...prev,
    contexto: { ...prev.contexto, documento_id: documentoId }
  }));
};

// Cuando se completa evaluación
const onEvaluacionComplete = (evaluacionId) => {
  setChatState(prev => ({
    ...prev,
    contexto: { ...prev.contexto, evaluacion_id: evaluacionId }
  }));
};
```

---

## 🎨 UI del Chat

### Diseño Sugerido

```jsx
<div className="chat-container">
  {/* Header */}
  <div className="chat-header">
    <span>🤖 EvaluAI Assistant</span>
    <span className="status">En línea</span>
  </div>
  
  {/* Mensajes */}
  <div className="chat-messages">
    {chatState.messages.map((msg, idx) => (
      <div key={idx} className={`message ${msg.role}`}>
        {msg.role === 'assistant' && <span className="avatar">🤖</span>}
        <div className="bubble">{msg.content}</div>
      </div>
    ))}
    {chatState.isLoading && <TypingIndicator />}
  </div>
  
  {/* Input */}
  <div className="chat-input">
    <input
      type="text"
      placeholder="Escribe tu mensaje..."
      onKeyPress={(e) => e.key === 'Enter' && sendMessage(e.target.value)}
    />
    <button onClick={() => sendMessage(inputValue)}>Enviar</button>
  </div>
</div>
```

---

## 🧩 Mensajes de Bienvenida Sugeridos

El agente puede iniciar la conversación con:

```
"¡Hola! Soy tu asistente de EvaluAI. Puedo ayudarte a:

📋 Configurar rúbricas personalizadas
📤 Evaluar documentos de estudiantes  
📊 Interpretar resultados de evaluaciones
💡 Sugerir mejoras a trabajos

¿Qué te gustaría hacer hoy?"
```

---

## ⚡ Quick Actions (Botones Rápidos)

Sugerir botones contextuales sobre el chat:

```jsx
const quickActions = [
  { label: "Evaluar documento", action: () => sendMessage("Quiero evaluar un documento") },
  { label: "Configurar rúbrica", action: () => sendMessage("Ayúdame con una rúbrica") },
  { label: "Ver mis evaluaciones", action: () => navigate('/evaluaciones') }
];
```

---

## 🔐 Seguridad

- El historial se mantiene solo en el frontend (no se persiste en backend)
- El contexto se envía en cada request para mantener estado
- No enviar información sensible de estudiantes en el chat

---

## 📝 Ejemplos de Prompts para el Usuario

Sugerir estos prompts en placeholder o botones:

- "Quiero evaluar un trabajo de matemáticas"
- "Configura una rúbrica para ensayos"
- "¿Cómo interpreto los resultados?"
- "¿Cuántas palabras me quedan?"
- "Ayúdame a mejorar esta evaluación"
