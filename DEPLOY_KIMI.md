# 🚀 Deploy con Kimi API (Moonshot AI)

## ✅ Cambios realizados

El backend ahora usa **Kimi API** con tu suscripción Allegretto:

| Componente | Valor |
|------------|-------|
| **API** | Moonshot (Kimi) |
| **Modelo** | kimi-k2-5 (Flagship) |
| **Base URL** | https://api.moonshot.cn/v1 |
| **Suscripción** | Allegretto |

## 📋 Pasos para Deploy

### 1. Crear API Key en Kimi (1 minuto)

En la imagen que me mostraste:

1. ✅ Estás en la consola correcta (console.moonshot.cn)
2. ✅ Tienes suscripción Allegretto activa
3. ✅ Haz clic en **"+ Create new API Key"**
4. ✅ Nombre: `EvaluAI-Backend`
5. ✅ **Copia la key** (solo se muestra una vez)

### 2. Configurar variables

```bash
# En backend/.env
KIMI_API_KEY=sk-la-key-que-copiaste
```

### 3. Deploy en Railway

```bash
cd backend

# Inicializar git
git init
git add .
git commit -m "MVP con Kimi API"

# Subir a Railway
railway login
railway link  # Selecciona tu proyecto
railway up
```

### 4. Configurar variables en Railway Dashboard

Ve a tu proyecto en railway.app → Variables:

```
KIMI_API_KEY=sk-tu-api-key
SECRET_KEY=una-clave-larga-aleatoria-de-32-caracteres-minimo
```

## 💰 Costo con tu suscripción Allegretto

| Concepto | Valor |
|----------|-------|
| Tu plan | Allegretto (ya pagado) |
| Uso actual | 1% semanal |
| Disponible | 99% restante |
| Costo adicional | $0 (ya está incluido) |
| **Margen tuyo** | **100%** 🎉 |

## 🧪 Probar después del deploy

```bash
# Health check
curl https://tu-app.up.railway.app/health

# Listar asignaturas
curl https://tu-app.up.railway.app/evaluaciones/asignaturas/lista
```

## ⚠️ IMPORTANTE

1. **La API Key solo se muestra una vez** al crearla en Kimi
2. **No compartas la key** (guárdala en variables de entorno)
3. **Tu suscripción Allegretto** cubre el uso del modelo K2.5
4. Si se te acaba el crédito, Kimi te avisa por email

## 📞 Si hay problemas

- Error 401: API Key inválida o expirada
- Error 429: Rate limit excedido (espera unos segundos)
- Error 500: Revisa logs en Railway Dashboard

---

**¿Creaste ya la API Key en Kimi?** Dame el OK y procedemos con el deploy final.
