
    console.log("prueba")
    const titleText = 'Subir CSV y Generar Nube de Palabras';
    const titleElement = document.getElementById('tituloTipeado');
    let index = 0;

    function typeWriter() {
        if (index < titleText.length) {
            titleElement.textContent += titleText.charAt(index);
            index++;
            setTimeout(typeWriter, 100);  // velocidad de escritura (en ms)
        }
    }

    window.onload = () => {
    typeWriter();

    // Control de input file personalizado
    const fileInput = document.getElementById('fileInput');
    const fileName = document.getElementById('fileName');
    const form = document.getElementById('uploadForm');
    const metricsDiv = document.getElementById('metrics');
    const wordcloudImage = document.getElementById('wordcloudImage');

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            fileName.textContent = fileInput.files[0].name;
        } else {
            fileName.textContent = 'Ningún archivo seleccionado';
        }
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (fileInput.files.length === 0) {
            alert('Por favor selecciona un archivo CSV.');
            return;
        }
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        metricsDiv.innerHTML = 'Procesando...';
        wordcloudImage.src = '';

        try {console.log('📤 Enviando POST a /upload');

            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
                
            });

            if (!response.ok) {
                const errorData = await response.json();
                metricsDiv.innerHTML = `<p style="color:red;">Error: ${errorData.error || 'Error desconocido'}</p>`;
                return;
            }

            const data = await response.json();

            wordcloudImage.src = data.image_url + '?t=' + new Date().getTime(); // evitar cache
            metricsDiv.innerHTML = `
                <p>Filas del CSV: ${data.metrics.filas}</p>
                <p>Columnas del CSV: ${data.metrics.columnas}</p>
                <p>Total de palabras: ${data.metrics.palabras_totales}</p>
            `;
        } catch (error) {
            metricsDiv.innerHTML = `<p style="color:red;">Error de conexión: ${error.message}</p>`;
        }
    });
};
