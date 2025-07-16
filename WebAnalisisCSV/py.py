from flask import Flask, render_template, request, jsonify
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# Ruta principal - carga el HTML
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para recibir el archivo CSV
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
     
    if file is None:
        print('❌ No se recibió ningún archivo')
        return jsonify({'error': 'No se recibió archivo'}), 400

    # Leer el CSV con pandas
    df = pd.read_csv(file)
    if df.empty:
            print('❌ CSV vacío')
            return jsonify({'error': 'El CSV está vacío'}), 400

    # Concatenar todo el texto del CSV en un solo string
    text_data = ' '.join(df.astype(str).values.flatten())

    # Generar la nube de palabras
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text_data)

    # Guardar la imagen en la carpeta /static
    image_path = os.path.join('static', 'wordcloud.png')
    wordcloud.to_file(image_path)

    # Calcular métricas básicas
    metrics = {
        'filas': int(df.shape[0]),
        'columnas': int(df.shape[1]),
        'palabras_totales': int(len(text_data.split()))
    }

    # Responder con JSON
    return jsonify({
        'image_url': '/static/wordcloud.png',
        'metrics': metrics
    })


if __name__ == '__main__':
    app.run(debug=True)