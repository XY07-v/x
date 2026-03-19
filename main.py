import pandas as pd
import requests
import io

URL = "https://manpowergroupcolombia-my.sharepoint.com/:x:/g/personal/edwar_vanegas_manpowercolombia_com/IQCFQVQEx44GSZgIu9VIZ2dGAS0h1sEo0V-hJ812-oW8tys?e=o0J3Aa&download=1"

def generar_reporte():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(URL, headers=headers, timeout=20)
        response.raise_for_status()
        
        # Leer datos: MES como texto
        df = pd.read_csv(io.BytesIO(response.content), sep=';', dtype={'MES': str}, encoding='latin1')

        # Reglas: Vacío = X, -1 = ✓
        df = df.astype(str).replace(['nan', 'None', '', 'nan.1'], 'X')
        df = df.replace(['-1', '-1.0'], '✓')

        # Diseño CSS para que se vea profesional
        estilo = """<style>
            body { font-family: sans-serif; margin: 30px; background-color: #f4f7f6; }
            table { border-collapse: collapse; width: 100%; background: white; }
            th { background: #004a99; color: white; padding: 10px; }
            td { padding: 8px; border: 1px solid #ddd; text-align: center; }
            .pos { color: #28a745; font-weight: bold; } /* Verde para ✓ */
            .def { color: #dc3545; font-weight: bold; } /* Rojo para X */
        </style>"""

        # Convertir a HTML y poner colores
        html_table = df.to_html(index=False, escape=False)
        html_table = html_table.replace('<td>✓</td>', '<td><span class="pos">✓</span></td>')
        html_table = html_table.replace('<td>X</td>', '<td><span class="def">X</span></td>')

        # Crear el archivo index.html final
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(f"<html><head><meta charset='UTF-8'>{estilo}</head><body>")
            f.write(f"<h2>Reporte Manpower (Lun-Sáb)</h2>{html_table}</body></html>")
        
        print("Reporte generado con éxito.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generar_reporte()
