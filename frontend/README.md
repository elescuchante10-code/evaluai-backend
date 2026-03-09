# EvaluAI Frontend

React frontend para EvaluAI Profesor

## Deploy en Vercel (Gratuito)

### Paso 1: Subir a GitHub

```bash
cd frontend
git init
git add .
git commit -m "Frontend v1.0"
git remote add origin https://github.com/elescuchante10-code/evaluai-frontend.git
git push -u origin main
```

### Paso 2: Conectar Vercel

1. Ve a https://vercel.com
2. Login con GitHub
3. "Add New Project"
4. Importar `evaluai-frontend`
5. Deploy automático

### Paso 3: Configurar variable de entorno

En Vercel Dashboard → Settings → Environment Variables:

```
REACT_APP_API_URL=https://web-production-83f44.up.railway.app
```

Redeploy.

---

## Desarrollo local

```bash
npm install
npm start
```

Abre http://localhost:3000
