import pandas as pd
import requests
import io

URL = "https://manpowergroupcolombia-my.sharepoint.com/:x:/g/personal/edwar_vanegas_manpowercolombia_com/IQCFQVQEx44GSZgIu9VIZ2dGAS0h1sEo0V-hJ812-oW8tys?e=o0J3Aa&download=1"

def generar_reporte():
    try:
        response = requests.get(URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
        df = pd.read_csv(io.BytesIO(response.content), sep=';', dtype={'MES': str}, encoding='latin1')

        # Aplicar tus reglas: Vacío = X, -1 = ✓
        df = df.astype(str).replace(['nan', 'None', '', 'nan.1'], 'X')
        df = df.replace(['-1', '-1.0'], '✓')

        # Generar la tabla HTML con colores
        html_table = df.to_html(index=False, escape=False)
        html_table = html_table.replace('<td>✓</td>', '<td><span class="positivo">✓</span></td>')
        html_table = html_table.replace('<td>X</td>', '<td><span class="deficit">X</span></td>')

        # EL TRUCO: Leer el index.html actual y reemplazar el texto de "Esperando..."
        with open("index.html", "r", encoding="utf-8") as f:
            contenido = f.read()

        # Reemplazamos el marcador por la tabla real
        marcador = '<div id="tabla-reporte">\n        <p style="text-align:center; color:#999;">Esperando actualización de datos desde SharePoint...</p>\n    </div>'
        nuevo_contenido = contenido.replace(marcador, f'<div id="tabla-reporte">{html_table}</div>')

        with open("index.html", "w", encoding="utf-8") as f:
            f.write(nuevo_contenido)
            
        print("Datos insertados correctamente.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generar_reporte()
