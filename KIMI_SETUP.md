# Configuración de Kimi AI (Moonshot)

## 🚀 Obtener API Key de Kimi

1. Ve a: https://platform.moonshot.cn
2. Crea una cuenta (puedes usar email o Google)
3. Ve a "API Keys" en el panel de control
4. Genera una nueva API Key
5. Copia la key (empieza con `sk-`)

## 💰 Precios de Kimi (Marzo 2025)

| Modelo | Input | Output |
|--------|-------|--------|
| **kimi-k2-5** | ¥1 / 1M tokens | ¥1 / 1M tokens |
| **kimi-k1-5** | ¥0.5 / 1M tokens | ¥0.5 / 1M tokens |

**Conversión:** ¥1 ≈ $0.14 USD ≈ $570 COP

**Ejemplo de costo:**
- Documento de 1500 palabras, 5 segmentos
- ~2000 tokens input + 2000 tokens output
- Costo: ~¥0.004 ≈ $2.3 COP

## ⚙️ Configuración en Railway

Variables de entorno necesarias:

```bash
AI_PROVIDER=kimi
KIMI_API_KEY=sk-tu_api_key_aqui
KIMI_MODEL=kimi-k2-5
SECRET_KEY=tu_secret_key_segura
```

### Pasos en Railway:

1. Ve a tu proyecto en Railway dashboard
2. Selecciona el servicio del backend
3. Ve a la pestaña "Variables"
4. Agrega las variables anteriores
5. Railway reiniciará automáticamente

## 🧪 Probar la conexión

```bash
curl -X POST https://web-production-83f44.up.railway.app/evaluaciones/procesar \
  -H "Authorization: Bearer TU_JWT_TOKEN" \
  -F "documento_id=xxx" \
  -F "asignatura=lenguaje"
```

## 🎯 Ventajas de Kimi

✅ **Excelente español** - Mejor que GPT-4 en muchos casos  
✅ **Precios bajos** - Muy económico para Latinoamérica  
✅ **Contexto largo** - Soporta hasta 200K tokens  
✅ **Razonamiento** - Bueno para evaluar matemáticas y ciencias  

## 🔧 Modelos disponibles

- `kimi-k2-5` - Recomendado (balance calidad/precio)
- `kimi-k1-5` - Más rápido, más económico
- `kimi-latest` - Última versión estable

## ⚠️ Notas importantes

1. **Crédito inicial:** Kimi suele dar ¥15 (~$8 USD) de crédito gratis
2. **Límite de rate:** 3 requests/segundo en plan gratuito
3. **Facturación:** Se cobra por tokens usados, no por request
4. **Regiones:** Servidores en Asia, latencia ~150ms desde Colombia

---

*Configurado para EvaluAI Profesor*
