# 📡 API Endpoints - EvaluAI Backend

**URL Base:** `https://web-production-83f44.up.railway.app`

**Autenticación:** Todas las rutas protegidas requieren header `Authorization: Bearer <token>`

---

## 🔐 1. AUTENTICACIÓN

### POST `/auth/register`
Registra un nuevo usuario (profesor)

**Request:**
```json
{
  "email": "profesor@ejemplo.com",
  "password": "contraseña123",
  "full_name": "Juan Pérez",
  "institution": "Colegio ABC"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Usuario registrado exitosamente",
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "profesor@ejemplo.com",
    "full_name": "Juan Pérez",
    "institution": "Colegio ABC",
    "words_available": 120000,
    "words_used": 0
  }
}
```

---

### POST `/auth/login`
Inicia sesión y obtiene token

**Request:**
```json
{
  "email": "profesor@ejemplo.com",
  "password": "contraseña123"
}
```

**Response (200):**
```json
{
  "success": true,
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "profesor@ejemplo.com",
    "full_name": "Juan Pérez",
    "words_available": 115000,
    "words_used": 5000,
    "extra_blocks": 0
  }
}
```

---

### POST `/auth/verify`
Verifica si un token es válido

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "success": true,
  "valid": true,
  "user_id": "uuid",
  "expires": 1234567890
}
```

---

### GET `/auth/me`
Obtiene información del usuario actual

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "success": true,
  "user": {
    "id": "uuid",
    "email": "profesor@ejemplo.com",
    "full_name": "Juan Pérez",
    "institution": "Colegio ABC",
    "words_available": 115000,
    "words_used": 5000,
    "extra_blocks": 0,
    "plan_type": "profesor",
    "is_active": true
  }
}
```

---

## 🤖 2. CHAT CON AGENTE IA

### POST `/agente/chat`
Envía un mensaje al agente IA

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request:**
```json
{
  "mensaje": "¿Cómo configuro una rúbrica para matemáticas?",
  "contexto": {
    "asignatura": "matematicas",
    "documento_id": "optional"
  },
  "historial": [
    {"role": "user", "content": "pregunta anterior"},
    {"role": "assistant", "content": "respuesta anterior"}
  ]
}
```

**Response (200):**
```json
{
  "success": true,
  "respuesta": "Para configurar una rúbrica de matemáticas...",
  "accion": "rubrica",
  "data": {
    "criterios_sugeridos": [
      {"nombre": "Procedimiento", "peso": 0.4},
      {"nombre": "Resultado", "peso": 0.3}
    ]
  }
}
```

**Acciones posibles:** `evaluar`, `rubrica`, `info`, `general`

---

### POST `/agente/sugerir-rubrica`
Solicita al agente una rúbrica sugerida

**Headers:**
```
Authorization: Bearer <token>
```

**Query Params:**
- `asignatura`: string (requerido)
- `tipo_trabajo`: string (opcional)
- `descripcion`: string (opcional)

**Response (200):**
```json
{
  "success": true,
  "asignatura": "matematicas",
  "tipo_trabajo": null,
  "rubrica": {
    "criterios": [
      {"nombre": "Procedimiento", "peso": 0.4, "descripcion": "..."},
      {"nombre": "Resultado", "peso": 0.3, "descripcion": "..."}
    ],
    "explicacion": "..."
  }
}
```

---

## 📄 3. DOCUMENTOS

### POST `/documentos/subir`
Sube un archivo (requiere autenticación)

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Data:**
- `archivo`: File (PDF, DOCX, TXT) - **requerido**
- `asignatura`: string - **requerido**
- `rubrica_json`: string (JSON) - opcional

**Response (200):**
```json
{
  "success": true,
  "estimacion": {
    "temp_id": "uuid",
    "filename": "trabajo.pdf",
    "word_count": 1500,
    "num_segmentos": 5,
    "asignatura": "matematicas",
    "texto_preview": "Primeros 500 caracteres...",
    "segmentos_preview": [...],
    "estimacion_costo": {
      "usd": 0.0025,
      "cop": 10.25,
      "tokens_input": 3500,
      "tokens_output": 1500
    }
  }
}
```

---

### GET `/documentos`
Lista los documentos del usuario

**Headers:**
```
Authorization: Bearer <token>
```

**Query Params:**
- `asignatura`: string (filtro opcional)
- `limit`: int (default: 50)
- `offset`: int (default: 0)

**Response (200):**
```json
{
  "success": true,
  "total": 25,
  "limit": 50,
  "offset": 0,
  "documentos": [
    {
      "id": "uuid",
      "filename": "trabajo.pdf",
      "asignatura": "matematicas",
      "calificacion_global": 8.5,
      "semaforo_global": "VERDE",
      "total_words": 1500,
      "total_segments": 5,
      "created_at": "2025-03-01T10:00:00",
      "cost_cop": 205.0
    }
  ]
}
```

---

### GET `/documentos/{documento_id}`
Obtiene detalle completo de un documento

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "success": true,
  "documento": {
    "id": "uuid",
    "filename": "trabajo.pdf",
    "asignatura": "matematicas",
    "tipo_trabajo": null,
    "calificacion_global": 8.5,
    "semaforo_global": "VERDE",
    "total_words": 1500,
    "total_segments": 5,
    "cost_cop": 205.0,
    "cost_usd": 0.05,
    "tokens_input": 2000,
    "tokens_output": 800,
    "created_at": "2025-03-01T10:00:00"
  },
  "resultados": {
    "segmentos": [...],
    "retroalimentacion_general": "..."
  }
}
```

---

### DELETE `/documentos/{documento_id}`
Elimina un documento

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "success": true,
  "message": "Documento eliminado exitosamente",
  "documento_id": "uuid"
}
```

---

### GET `/documentos/{documento_id}/resumen`
Obtiene resumen rápido para el dashboard

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "success": true,
  "resumen": {
    "id": "uuid",
    "filename": "trabajo.pdf",
    "asignatura": "matematicas",
    "calificacion_global": 8.5,
    "semaforo_global": "VERDE",
    "total_segments": 5,
    "distribucion_semaforos": {
      "VERDE": 4,
      "AMARILLO": 1,
      "ROJO": 0
    },
    "fortalezas": ["Procedimiento claro", "Buena notación"],
    "areas_mejora": ["Revisar cálculos"]
  }
}
```

---

## ✅ 4. EVALUACIÓN

### POST `/evaluaciones/procesar`
Procesa un documento con IA (formato del dashboard)

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Data:**
- `documento_id`: string (temp_id de /subir) - **requerido**
- `asignatura`: string - **requerido**
- `rubrica`: string (JSON) - opcional

**Response (200):**
```json
{
  "success": true,
  "id": "uuid-evaluacion",
  "estado": "completado",
  "calificacion_global": 8.5,
  "segmentos": [
    {
      "id": 1,
      "tipo": "ejercicio",
      "calificacion": 9.0,
      "semaforo": "VERDE",
      "retroalimentacion": "Excelente trabajo",
      "criterios": [...]
    }
  ],
  "retroalimentacion": "El estudiante demuestra buen dominio del tema.",
  "evaluacion": { /* datos completos */ }
}
```

---

### POST `/evaluaciones/evaluar`
Ejecuta evaluación (versión alternativa)

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Data:**
- `estimacion_id`: string - **requerido**
- `confirmar`: bool (default: true)
- `user_id`: string - **requerido** (será removido, usar token)

**Response (200):**
```json
{
  "success": true,
  "evaluacion": {
    "id": "uuid",
    "message": "Evaluación completada",
    "user_words_remaining": 115000,
    "calificacion_global": 8.5,
    "semaforo_global": "VERDE",
    "segmentos": [...]
  }
}
```

---

### GET `/evaluaciones/{evaluacion_id}`
Obtiene una evaluación por ID

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "filename": "trabajo.pdf",
    "asignatura": "matematicas",
    "calificacion_global": 8.5,
    "semaforo_global": "VERDE",
    "total_segments": 5,
    "total_words": 1500,
    "created_at": "2025-03-01T10:00:00",
    "cost_cop": 205.0
  },
  "detalle": { /* resultados_json completo */ }
}
```

---

### GET `/evaluaciones/{evaluacion_id}/reporte?formato=json|word`
Descarga reporte de evaluación

**Headers:**
```
Authorization: Bearer <token>
```

**Query Params:**
- `formato`: `json` o `word` (default: json)

**Response JSON (200):**
```json
{
  "segmentos": [...],
  "retroalimentacion_general": "..."
}
```

**Response Word (200):**
Archivo `.docx` descargable

---

### GET `/evaluaciones/asignaturas/lista`
Lista asignaturas soportadas (público)

**Response (200):**
```json
{
  "asignaturas": [
    {"id": "matematicas", "nombre": "Matemáticas", "icono": "📐"},
    {"id": "lenguaje", "nombre": "Lengua Castellana", "icono": "📚"},
    {"id": "sociales", "nombre": "Ciencias Sociales", "icono": "🌍"},
    {"id": "ingles", "nombre": "Inglés", "icono": "🗣️"},
    {"id": "ciencias", "nombre": "Ciencias Naturales", "icono": "🔬"},
    {"id": "generico", "nombre": "Otra (segmentación básica)", "icono": "📝"}
  ]
}
```

---

## 📊 RESUMEN DE ENDPOINTS

| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| POST | `/auth/register` | ❌ | Crear cuenta |
| POST | `/auth/login` | ❌ | Iniciar sesión |
| POST | `/auth/verify` | ✅ | Verificar token |
| GET | `/auth/me` | ✅ | Info usuario |
| POST | `/agente/chat` | ✅ | Chat con IA |
| POST | `/agente/sugerir-rubrica` | ✅ | Sugerir rúbrica |
| POST | `/documentos/subir` | ✅ | Subir archivo |
| GET | `/documentos` | ✅ | Listar documentos |
| GET | `/documentos/{id}` | ✅ | Ver documento |
| DELETE | `/documentos/{id}` | ✅ | Eliminar documento |
| POST | `/evaluaciones/procesar` | ✅ | Procesar con IA |
| GET | `/evaluaciones/asignaturas/lista` | ❌ | Listar asignaturas |

---

## ⚠️ CÓDIGOS DE ERROR

| Código | Significado |
|--------|-------------|
| 200 | OK |
| 201 | Creado |
| 400 | Bad Request (datos inválidos) |
| 401 | Unauthorized (token inválido/faltante) |
| 404 | Not Found |
| 500 | Error del servidor |

---

## 📝 NOTAS PARA EL FRONTEND

1. **Guardar el token:** Al hacer login/register, guardar `access_token` en localStorage
2. **Enviar token:** Incluir en header `Authorization: Bearer <token>` en todas las peticiones protegidas
3. **Renovar token:** El token expira en 7 días, redirigir a login si recibes 401
4. **Flujo de evaluación:**
   - 1. POST `/documentos/subir` → obtienes estimación
   - 2. POST `/evaluaciones/procesar` → ejecutas evaluación
   - 3. GET `/documentos/{id}` → obtienes resultados completos
