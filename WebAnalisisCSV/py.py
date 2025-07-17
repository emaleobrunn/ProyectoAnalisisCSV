from flask import Flask, render_template, request, jsonify
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os

# Configuración inicial
app = Flask(__name__)

# Ruta base del proyecto (donde está py.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ruta absoluta de la carpeta static
STATIC_FOLDER = os.path.join(BASE_DIR, 'static')

# Asegurarse que la carpeta static existe
os.makedirs(STATIC_FOLDER, exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        file = request.files.get('file')

        if not file:
            return jsonify({'error': 'No se recibió archivo'}), 400

        # Leer CSV - intentar con delimitador coma y saltar líneas defectuosas
        try:
            df = pd.read_csv(file, delimiter=',', on_bad_lines='skip')
        except Exception as e:
            print('❌ Error leyendo CSV:', str(e))
            return jsonify({'error': 'El archivo CSV es inválido o está corrupto.'}), 400

        if df.empty:
            return jsonify({'error': 'El CSV está vacío'}), 400

        # Concatenar todo el texto en un único string
        text_data = ' '.join(df.astype(str).values.flatten())

        # Generar la nube de palabras
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text_data)

        # Guardar la imagen en static
        image_path = os.path.join(STATIC_FOLDER, 'wordcloud.png')
        wordcloud.to_file(image_path)

        # Métricas básicas
        metrics = {
            'filas': int(df.shape[0]),
            'columnas': int(df.shape[1]),
            'palabras_totales': int(len(text_data.split()))
        }

        # Devolver ruta pública de la imagen
        return jsonify({
            'image_url': '/static/wordcloud.png',
            'metrics': metrics
        })

    except Exception as e:
        print('🔥 ERROR INTERNO en /upload:', str(e))
        return jsonify({'error': 'Error interno: ' + str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)