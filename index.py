import pandas as pd
import requests
import io
from datetime import datetime

# URL de SharePoint
URL_DATA = "https://manpowergroupcolombia-my.sharepoint.com/:x:/g/personal/edwar_vanegas_manpowercolombia_com/IQCFVQXe44GSZglu9VIZ2dGAS0h1seOoV-hJ812-oW8tys?e=o0J3Aa&download=1"

def generar_reporte():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(URL_DATA, headers=headers, timeout=30)
        
        # 1. MES como texto y carga de datos
        df = pd.read_csv(io.BytesIO(r.content), sep=';', encoding='latin1', dtype={'MES': str})
        
        # 2. Lógica de fechas (Lunes a Sábado, solo hasta hoy)
        df['Fecha_DT'] = pd.to_datetime(df['Fecha'], errors='coerce')
        df = df[df['Fecha_DT'] <= datetime.now()].copy()
        
        # 3. Reglas: -1 es positivo (✔️), vacío es déficit (❌)
        df = df.fillna('❌')
        df = df.replace(['-1', '-1.0', -1], '✔️')
        
        df = df.sort_values(by='Fecha_DT', ascending=False).drop(columns=['Fecha_DT'])

        # 4. Diseño de la tabla con Buscador
        html_tabla = df.to_html(index=False, table_id="tablaDatos", border=0)
        html_final = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Reporte Manpower</title>
            <style>
                body {{ font-family: sans-serif; margin: 20px; background: #f4f7f9; }}
                .card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                input {{ padding: 10px; width: 300px; border-radius: 5px; border: 1px solid #ccc; }}
                button {{ padding: 10px; background: #002d5a; color: white; border: none; border-radius: 5px; cursor: pointer; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th {{ background: #002d5a; color: white; padding: 10px; text-align: left; }}
                td {{ padding: 8px; border-bottom: 1px solid #eee; }}
                .v {{ color: green; font-weight: bold; font-size: 1.1em; }}
                .x {{ color: red; font-weight: bold; font-size: 1.1em; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h2>📊 Reporte de Gestión Manpower</h2>
                <input type="text" id="busc" placeholder="Escribe el nombre del empleado...">
                <button onclick="buscar()">🔍 BUSCAR</button>
                <div style="overflow-x:auto;">{html_tabla}</div>
            </div>
            <script>
                function buscar() {{
                    var input = document.getElementById("busc").value.toUpperCase();
                    var rows = document.getElementById("tablaDatos").getElementsByTagName("tr");
                    for (var i = 1; i < rows.length; i++) {{
                        var name = rows[i].cells[4] ? rows[i].cells[4].innerText.toUpperCase() : "";
                        rows[i].style.display = name.includes(input) ? "" : "none";
                    }}
                }}
            </script>
        </body>
        </html>
        """.replace('✔️', '<span class="v">✔️</span>').replace('❌', '<span class="x">❌</span>')

        # ESTA LÍNEA SOBREESCRIBE EL HTML VIEJO AUTOMÁTICAMENTE
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_final)
        print("¡Reporte actualizado con éxito!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generar_reporte()
