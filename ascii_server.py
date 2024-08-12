import os
import requests
from flask import Flask, request, jsonify
from PIL import Image, UnidentifiedImageError
from io import BytesIO

app = Flask(__name__)

# Configurar el puerto desde una variable de entorno
puerto = int(os.environ.get("PUERTO_SERVIDOR", 5000))

# Definir los caracteres para la conversión a ASCII
ASCII_CHARS = "@%#*+=-:. "

def convert_to_ascii(image, ancho, alto):
    # Redimensionar la imagen
    width, height = image.size
    
    if ancho is None and alto is None:
        aspect_ratio = height / width
        ancho = 100  # Ancho por defecto
        alto = int(aspect_ratio * ancho * 0.55)
        
        # Ajustar para un máximo de 20 líneas
        if alto > 20:
            alto = 20
            ancho = int(alto / (aspect_ratio * 0.55))
    else:
        aspect_ratio = height / width
        if ancho is None:
            ancho = int(alto / (aspect_ratio * 0.55))
        if alto is None:
            alto = int(aspect_ratio * ancho * 0.55)
    
    image = image.resize((ancho, alto))
    
    # Convertir la imagen a escala de grises
    image = image.convert('L')
    
    # Mapear los píxeles a caracteres ASCII
    pixels = image.getdata()
    ascii_str = "".join([ASCII_CHARS[pixel // 32] for pixel in pixels])
    
    # Dividir el string ASCII en líneas
    ascii_str_len = len(ascii_str)
    ascii_img = "\n".join([ascii_str[i:i+ancho] for i in range(0, ascii_str_len, ancho)])
    
    return ascii_img

@app.route('/convertir', methods=['GET'])
def convertir():
    image_url = request.args.get('url')
    ancho = request.args.get('ancho', type=int)
    alto = request.args.get('alto', type=int)
    
    if not image_url:
        return jsonify({"error": "No se proporcionó la URL de la imagen"}), 400

    try:
        # Descargar la imagen desde la URL proporcionada
        response = requests.get(image_url)
        response.raise_for_status()  # Asegurarse de que la solicitud fue exitosa
        
        # Intentar abrir la imagen directamente
        image = Image.open(BytesIO(response.content))
        
        # Convertir la imagen a ASCII
        ascii_img = convert_to_ascii(image, ancho, alto)
        
        # Devolver la imagen en formato ASCII
        return ascii_img
    
    except UnidentifiedImageError:
        return jsonify({"error": "No se pudo identificar el archivo de imagen"}), 400
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error al descargar la imagen: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=puerto)
