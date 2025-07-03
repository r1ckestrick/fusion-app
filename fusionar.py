import os
import cv2
import cv2.data  # Asegura que cv2.data existe
from PIL import Image, ImageDraw
import openai
import uuid
from typing import Literal

# Configura tu API Key de OpenAI desde variables de entorno
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required")

openai.api_key = api_key

TEMP_FOLDER = os.path.join(os.path.dirname(__file__), "temp")
os.makedirs(TEMP_FOLDER, exist_ok=True)

def crear_mascara_ovalada_centrada(size=512):
    mask = Image.new("L", (size, size), 0)  # 'L' = escala de grises, fondo negro
    draw = ImageDraw.Draw(mask)
    cx, cy = size // 2, size // 2
    bbox = [cx - 50, cy - 100, cx + 50, cy + 100]  # óvalo 100x200 px
    draw.ellipse(bbox, fill=255)  # blanco puro
    mask_path = os.path.join(TEMP_FOLDER, f"mask_{uuid.uuid4().hex}.png")
    mask.save(mask_path, "PNG")
    return mask_path

def editar_imagen_dalle2(ruta_imagen, ruta_mascara, prompt):
    import base64
    with open(ruta_imagen, "rb") as image_file, open(ruta_mascara, "rb") as mask_file:
        response = openai.images.edit(
            model="dall-e-2",
            image=image_file,
            mask=mask_file,
            prompt=prompt,
            n=1,
            size="512x512",
            response_format="b64_json"
        )
    if not hasattr(response, 'data') or not response.data:
        raise Exception("No se recibió una respuesta válida de la API de OpenAI")
    b64_img = getattr(response.data[0], 'b64_json', None)
    if not b64_img:
        raise Exception("No se recibió una imagen base64 de la API de OpenAI")
    output_filename = f"fusion_{uuid.uuid4().hex}.png"
    output_path = os.path.join(TEMP_FOLDER, output_filename)
    with open(output_path, "wb") as f:
        f.write(base64.b64decode(b64_img))
    return output_path

def editar_imagen_gpt_image1_sin_mascara(ruta_imagen, prompt):
    import base64
    with open(ruta_imagen, "rb") as image_file:
        response = openai.images.edit(
            model="gpt-image-1",
            image=image_file,
            prompt=prompt,
            n=1,
            size="1024x1024",
            quality="low",
            output_format="png",
            background="auto"
        )
    if not hasattr(response, 'data') or not response.data:
        raise Exception("No se recibió una respuesta válida de la API de OpenAI")
    b64_img = getattr(response.data[0], 'b64_json', None)
    if not b64_img:
        raise Exception("No se recibió una imagen base64 de la API de OpenAI")
    output_filename = f"fusion_{uuid.uuid4().hex}.png"
    output_path = os.path.join(TEMP_FOLDER, output_filename)
    with open(output_path, "wb") as f:
        f.write(base64.b64decode(b64_img))
    return output_path

def preparar_imagen_cuadrada(ruta_entrada, ruta_salida, size=1024):
    img = Image.open(ruta_entrada).convert("RGBA")
    min_side = min(img.width, img.height)
    left = (img.width - min_side) // 2
    top = (img.height - min_side) // 2
    right = left + min_side
    bottom = top + min_side
    img_cropped = img.crop((left, top, right, bottom))
    try:
        resample = Image.Resampling.LANCZOS
    except AttributeError:
        resample = 1  # LANCZOS
    img_resized = img_cropped.resize((size, size), resample)
    img_resized.save(ruta_salida, "PNG")
    return ruta_salida

def componer_inpainting(original_path, generado_path, mask_path, output_path):
    original = Image.open(original_path).convert("RGBA")
    generado = Image.open(generado_path).convert("RGBA")
    mask = Image.open(mask_path).convert("L")
    generado = generado.resize(original.size)
    mask = mask.resize(original.size)
    resultado = Image.composite(generado, original, mask)
    resultado.save(output_path, "PNG")
    return output_path

def fusionar_rostros(input_path: str, prompt: str = "") -> str:
    """
    Fusiona rostros usando OpenAI DALL-E 2
    Args:
        input_path: Ruta de la imagen de entrada
        prompt: Prompt para DALL-E 2 (opcional)
    Returns:
        Ruta local de la imagen generada
    Raises:
        FileNotFoundError, Exception
    """
    if not input_path or not isinstance(input_path, str):
        raise ValueError("input_path must be a non-empty string")

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Imagen no encontrada: {input_path}")

    prompt = prompt or "In the masked area between both faces, generate a subtle skin deformation, stretching and blending both sides together like organic slime. The fusion should feel organic and slightly surreal, it should look melted together, the rest of the image should be the same as the original"

    # Prepara imagen cuadrada PNG 1024x1024
    cuadrada_path = os.path.join(TEMP_FOLDER, f"cuadrada_{uuid.uuid4().hex}.png")
    preparar_imagen_cuadrada(input_path, cuadrada_path, size=1024)

    # Usa gpt-image-1 sin máscara
    output_path = editar_imagen_gpt_image1_sin_mascara(cuadrada_path, prompt)
    if not output_path or not isinstance(output_path, str) or output_path.strip() == "" or not os.path.exists(output_path):
        raise Exception("No se obtuvo una imagen generada")

    return output_path
