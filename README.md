# 🚀 EvaluAI Backend - Guía Rápida

## Deploy en Railway (5 minutos)

### 1. Preparar código
```bash
cd backend
git init
git add .
git commit -m "Primer commit"
```

### 2. Crear proyecto Railway
```bash
# Instalar CLI de Railway
npm install -g @railway/cli

# Login
railway login

# Crear proyecto
railway init --name evaluai-backend
```

### 3. Configurar variables de entorno
En el dashboard de Railway, agrega:
```
DEEPSEEK_API_KEY=sk-tu-api-key
SECRET_KEY=clave-secreta-minimo-32-caracteres
```

### 4. Deploy
```bash
railway up
```

¡Listo! Tu API estará en: `https://evaluai-backend.up.railway.app`

---

## Ejecutar Local (Desarrollo)

### 1. Instalar dependencias
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

pip install -r requirements.txt
```

### 2. Configurar .env
```bash
cp .env .env.local
# Editar .env.local con tu DEEPSEEK_API_KEY
```

### 3. Ejecutar
```bash
python main.py
```

API en: `http://localhost:8000`
Docs en: `http://localhost:8000/docs`

---

## API Endpoints

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/health` | GET | Verificar estado |
| `/evaluaciones/asignaturas/lista` | GET | Listar asignaturas |
| `/evaluaciones/subir` | POST | Subir documento |
| `/evaluaciones/evaluar` | POST | Ejecutar evaluación |
| `/evaluaciones/{id}` | GET | Ver evaluación |

---

## Prueba rápida

```bash
# Health check
curl https://tu-app.up.railway.app/health

# Listar asignaturas
curl https://tu-app.up.railway.app/evaluaciones/asignaturas/lista
```
