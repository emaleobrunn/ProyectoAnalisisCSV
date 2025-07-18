from flask import Flask, render_template, request, jsonify
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
import numpy as np

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
def detectar_instituciones(df):
    """
    Dado un DataFrame del Excel cargado, detecta las instituciones y separa los bloques.
    Retorna un diccionario {nombre_institución: DataFrame correspondiente}.
    """
    instituciones = {}
    current_institucion = None
    datos_actuales = []

    for index, row in df.iterrows():
        valores = [str(val) for val in row if pd.notna(val)]
        linea_texto = ' '.join(valores).upper()

        if "INSTITUCION" in linea_texto:
            # Si ya había una institución previa, la guardamos
            if current_institucion and datos_actuales:
                instituciones[current_institucion] = pd.DataFrame(datos_actuales)

            # Nueva institución detectada
            nombre = linea_texto.split(':')[-1].strip()
            current_institucion = nombre if nombre else f"INSTITUCION_DESCONOCIDA_{len(instituciones)+1}"
            datos_actuales = []
            continue

        # Si ya detectamos una institución, agregamos la fila
        if current_institucion:
            datos_actuales.append(row)

    # Guardar el último bloque
    if current_institucion and datos_actuales:
        instituciones[current_institucion] = pd.DataFrame(datos_actuales)

    return instituciones

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        file = request.files.get('file')

        if not file:
            return jsonify({'error': 'No se recibió archivo'}), 400


        filename = file.filename.lower()

        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(file, delimiter=',', on_bad_lines='skip')
            elif filename.endswith('.xlsx'):
                df = pd.read_excel(file)
            else:
                return jsonify ({'error': 'Formato no soportando, subi un CSV o un XLSX'})
        except Exception as e:
            print('❌ Error leyendo CSV:', str(e))
            return jsonify({'error': 'El archivo CSV es inválido o está corrupto.'}), 400

        if df.empty:
            return jsonify({'error': 'El CSV está vacío'}), 400

          # Detectar instituciones y separarlas
        instituciones = detectar_instituciones(df)
        print(f'🔍 Se detectaron {len(instituciones)} instituciones.')

        # Para la demo: usar la primera institución encontrada
        primera_institucion = next(iter(instituciones.keys()))
        df_institucion = instituciones[primera_institucion]


        # Concatenar todo el texto en un único string
        text_data = ' '.join(df.astype(str).values.flatten())

        # Generar la nube de palabras
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text_data)

        # Guardar la imagen en static
        image_path = os.path.join(STATIC_FOLDER, 'wordcloud.png')
        wordcloud.to_file(image_path)

        # Métricas básicas
        metrics = {
            'institucion': primera_institucion,
            'filas': int(df_institucion.shape[0]),
            'columnas': int(df_institucion.shape[1]),
            'palabras_totales': int(len(text_data.split()))
            
        }
        print(df.columns)
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