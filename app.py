from flask import Flask, request, render_template, send_file, flash, redirect, url_for, jsonify
from fusionar import fusionar_rostros
import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
import logging
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configuración
COMFYUI_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ComfyUI'))
UPLOAD_FOLDER = os.path.join('..', 'ComfyUI', 'temp')
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 10 * 1024 * 1024))  # 10MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
COMFY_URL = os.getenv('COMFY_URL', 'http://127.0.0.1:8188')

# Crear directorios necesarios
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image(file_path):
    """Valida que el archivo sea una imagen válida"""
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except Exception as e:
        logger.error(f"Error validando imagen {file_path}: {e}")
        return False

def cleanup_temp_files():
    """Limpia archivos temporales antiguos (más de 1 hora)"""
    try:
        current_time = datetime.now()
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                if (current_time - file_time).total_seconds() > 3600:  # 1 hora
                    os.remove(file_path)
                    logger.info(f"Archivo temporal eliminado: {filename}")
    except Exception as e:
        logger.error(f"Error limpiando archivos temporales: {e}")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Verificar si se envió un archivo
        if 'image' not in request.files:
            return jsonify({
                "success": False,
                "error": "No se seleccionó ningún archivo"
            })
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({
                "success": False,
                "error": "No se seleccionó ningún archivo"
            })
        
        # Verificar tamaño del archivo
        file.seek(0, 2)  # Ir al final del archivo
        file_size = file.tell()
        file.seek(0)  # Volver al inicio
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({
                "success": False,
                "error": f'El archivo es demasiado grande. Máximo {MAX_FILE_SIZE // (1024*1024)}MB'
            })
        
        # Verificar extensión
        if not allowed_file(file.filename):
            return jsonify({
                "success": False,
                "error": f'Tipo de archivo no permitido. Formatos válidos: {", ".join(ALLOWED_EXTENSIONS)}'
            })
        
        # Generar nombre único para el archivo
        filename = f"{uuid.uuid4().hex}.png"
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        
        try:
            # Guardar archivo
            file.save(input_path)
            
            # Validar que sea una imagen válida
            if not validate_image(input_path):
                os.remove(input_path)
                return jsonify({
                    "success": False,
                    "error": "El archivo no es una imagen válida"
                })
            
            # Depuración extra
            print("Ruta de imagen recibida:", input_path)
            print("¿Existe?", os.path.exists(input_path))
            from PIL import Image
            try:
                with Image.open(input_path) as img:
                    img.verify()
                print("Imagen válida")
            except Exception as e:
                print("Imagen inválida:", e)
            
            # Usar ruta absoluta para fusionar_rostros
            abs_input_path = os.path.abspath(input_path)
            output_path = fusionar_rostros(abs_input_path)
            
            # Limpiar archivo temporal
            if os.path.exists(input_path):
                os.remove(input_path)
                logger.info(f"Archivo temporal eliminado: {filename}")
            
            # Limpiar archivos temporales antiguos
            cleanup_temp_files()
            
            # Convertir ruta absoluta a ruta relativa para servir
            relative_output_path = os.path.relpath(output_path, os.path.dirname(__file__))
            relative_output_path = relative_output_path.replace("\\", "/")
            
            return jsonify({
                "success": True,
                "image_path": f"/temp/{os.path.basename(output_path)}"
            })
            
        except Exception as e:
            # Limpiar archivo temporal en caso de error
            if os.path.exists(input_path):
                os.remove(input_path)
            
            logger.error(f"Error procesando imagen {filename}: {e}")
            return jsonify({
                "success": False,
                "error": f'Error al procesar la imagen: {str(e)}'
            })

    return render_template("index.html")

@app.route("/temp/<filename>")
def serve_temp_file(filename):
    """Sirve archivos desde la carpeta temp/"""
    temp_folder = os.path.join(os.path.dirname(__file__), "temp")
    return send_file(os.path.join(temp_folder, filename), mimetype="image/png")

@app.route("/health")
def health_check():
    """Endpoint para verificar el estado del servicio"""
    try:
        # Verificar conexión con ComfyUI
        import requests
        response = requests.get(f"{COMFY_URL}/system_stats", timeout=5)
        comfy_status = "connected" if response.status_code == 200 else "disconnected"
    except:
        comfy_status = "disconnected"
    
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "comfyui_status": comfy_status,
        "temp_files_count": len(os.listdir(UPLOAD_FOLDER))
    })

@app.errorhandler(413)
def too_large(e):
    """Maneja archivos demasiado grandes"""
    flash('El archivo es demasiado grande', 'error')
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_error(e):
    """Maneja errores internos del servidor"""
    logger.error(f"Error interno del servidor: {e}")
    flash('Error interno del servidor. Inténtalo de nuevo.', 'error')
    return redirect(url_for('index'))

if __name__ == "__main__":
    # Limpiar archivos temporales al iniciar
    cleanup_temp_files()
    
    debug_mode = os.getenv('DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('PORT', 7860))
    
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
