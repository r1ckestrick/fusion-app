# 🚀 Guía de Despliegue - Fusion App

## 📋 Opciones de Despliegue

### 1. **Vercel (RECOMENDADO)**

#### Ventajas:
- ⚡ Despliegue súper rápido
- 🌍 CDN global automático
- 🔒 SSL automático
- 💰 Gratis para proyectos personales
- 🔄 Integración perfecta con GitHub

#### Pasos para desplegar en Vercel:

1. **Preparar el repositorio:**
   ```bash
   git add .
   git commit -m "Preparar para despliegue"
   git push origin main
   ```

2. **Conectar con Vercel:**
   - Ve a [vercel.com](https://vercel.com)
   - Conecta tu cuenta de GitHub
   - Importa tu repositorio

3. **Configurar variables de entorno en Vercel:**
   - Ve a Settings → Environment Variables
   - Añade:
     ```
     OPENAI_API_KEY=tu_api_key_real_aqui
     SECRET_KEY=una_clave_secreta_muy_larga_y_compleja
     DEBUG=False
     ```

4. **Desplegar:**
   - Vercel detectará automáticamente que es una app Python
   - El despliegue se hará automáticamente

### 2. **Railway**

#### Ventajas:
- 🎯 Muy fácil de usar
- 🔒 Variables de entorno seguras
- ⚡ Sin límites de tiempo de ejecución
- 📈 Escalado automático

#### Pasos para desplegar en Railway:

1. **Instalar Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Conectar con Railway:**
   ```bash
   railway login
   railway init
   ```

3. **Configurar variables de entorno:**
   ```bash
   railway variables set OPENAI_API_KEY=tu_api_key_real_aqui
   railway variables set SECRET_KEY=una_clave_secreta_muy_larga_y_compleja
   railway variables set DEBUG=False
   ```

4. **Desplegar:**
   ```bash
   railway up
   ```

### 3. **Render**

#### Ventajas:
- 🛡️ Muy estable y confiable
- 🔒 Variables de entorno seguras
- ⚡ Sin límites de tiempo
- 🔒 SSL automático

#### Pasos para desplegar en Render:

1. **Crear cuenta en Render:**
   - Ve a [render.com](https://render.com)
   - Crea una cuenta

2. **Crear nuevo Web Service:**
   - Conecta tu repositorio de GitHub
   - Selecciona Python como runtime

3. **Configurar:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`
   - Environment Variables:
     ```
     OPENAI_API_KEY=tu_api_key_real_aqui
     SECRET_KEY=una_clave_secreta_muy_larga_y_compleja
     DEBUG=False
     ```

## 🔐 Seguridad de API Keys

### ❌ NUNCA hagas esto:
```python
# MAL - Nunca hardcodees tu API key
openai.api_key = "sk-proj-..."
```

### ✅ SIEMPRE haz esto:
```python
# BIEN - Usa variables de entorno
import os
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required")
openai.api_key = api_key
```

### 🔒 Configuración segura:

1. **Genera una nueva API key:**
   - Ve a [platform.openai.com](https://platform.openai.com)
   - Crea una nueva API key
   - **IMPORTANTE:** Revoca la key anterior que estaba en el código

2. **Configura variables de entorno:**
   - En tu plataforma de despliegue, añade:
     ```
     OPENAI_API_KEY=tu_nueva_api_key_aqui
     ```

3. **Verifica que no esté en el código:**
   - Busca en todo tu código por "sk-proj-"
   - Asegúrate de que no aparezca en ningún lugar

## 🧪 Testing Local

Antes de desplegar, prueba localmente:

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar variables de entorno:**
   ```bash
   # En Windows PowerShell:
   $env:OPENAI_API_KEY="tu_api_key_aqui"
   $env:SECRET_KEY="tu_secret_key_aqui"
   
   # En Linux/Mac:
   export OPENAI_API_KEY="tu_api_key_aqui"
   export SECRET_KEY="tu_secret_key_aqui"
   ```

3. **Ejecutar la aplicación:**
   ```bash
   python app.py
   ```

## 📊 Monitoreo

### Health Check:
Tu app incluye un endpoint de health check:
```
GET /health
```

### Logs:
- Vercel: Dashboard → Functions → Logs
- Railway: `railway logs`
- Render: Dashboard → Logs

## 🚨 Troubleshooting

### Error: "OPENAI_API_KEY environment variable is required"
- Verifica que la variable esté configurada en tu plataforma de despliegue
- Asegúrate de que el nombre sea exactamente `OPENAI_API_KEY`

### Error: "Request timeout"
- Vercel tiene límite de 10 segundos
- Considera usar Railway o Render para procesamiento más largo

### Error: "Module not found"
- Verifica que todas las dependencias estén en `requirements.txt`
- Asegúrate de que las versiones sean compatibles

## 🌟 Recomendación Final

**Para tu caso específico, recomiendo Vercel** porque:
1. Tu app es relativamente simple
2. El procesamiento de imágenes no debería tomar más de 10 segundos
3. Tendrás la mejor velocidad global
4. Es gratis para proyectos personales

¡Tu app estará disponible worldwide en minutos! 🚀 