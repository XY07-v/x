import pandas as pd
import requests
import io
from datetime import datetime

URL_DATA = "https://manpowergroupcolombia-my.sharepoint.com/:x:/g/personal/edwar_vanegas_manpowercolombia_com/IQCFVQXe44GSZglu9VIZ2dGAS0h1seOoV-hJ812-oW8tys?e=o0J3Aa&download=1"

def generar_reporte():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(URL_DATA, headers=headers, timeout=30)
        
        # Carga (MES como texto)
        df = pd.read_csv(io.BytesIO(r.content), sep=';', encoding='latin1', dtype={'MES': str})
        
        # Filtro: Solo hasta hoy (Lunes a Sábado)
        df['Fecha_DT'] = pd.to_datetime(df['Fecha'], errors='coerce')
        df = df[df['Fecha_DT'] <= datetime.now()].copy()
        
        # Lógica de iconos
        df = df.fillna('❌').replace(['-1', '-1.0', -1], '✔️')
        df = df.sort_values(by='Fecha_DT', ascending=False).drop(columns=['Fecha_DT'])

        html_tabla = df.to_html(index=False, table_id="tablaDatos", border=0)
        html_final = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Reporte Manpower</title>
            <style>
                body {{ font-family: sans-serif; margin: 20px; background: #f4f7f9; }}
                .card {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
                input {{ padding: 12px; width: 300px; border-radius: 8px; border: 1px solid #ccc; font-size: 16px; }}
                button {{ padding: 12px 20px; background: #002d5a; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; display: none; }}
                th {{ background: #002d5a; color: white; padding: 12px; text-align: left; }}
                td {{ padding: 10px; border-bottom: 1px solid #eee; }}
                .v {{ color: green; font-weight: bold; font-size: 1.2em; }}
                .x {{ color: red; font-weight: bold; font-size: 1.2em; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h2>📊 Gestión Operativa Manpower</h2>
                <input type="text" id="busc" placeholder="Escribe el nombre del empleado...">
                <button onclick="buscar()">🔍 VER / BUSCAR</button>
                <div style="overflow-x:auto;">{html_tabla}</div>
            </div>
            <script>
                function buscar() {{
                    var input = document.getElementById("busc").value.toUpperCase();
                    var table = document.getElementById("tablaDatos");
                    var rows = table.getElementsByTagName("tr");
                    table.style.display = "table"; 
                    for (var i = 1; i < rows.length; i++) {{
                        var name = rows[i].cells[4] ? rows[i].cells[4].innerText.toUpperCase() : "";
                        rows[i].style.display = name.includes(input) ? "" : "none";
                    }}
                }}
            </script>
        </body>
        </html>
        """.replace('✔️', '<span class="v">✔️</span>').replace('❌', '<span class="x">❌</span>')

        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_final)
        print("✅ Éxito: index.html actualizado.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generar_reporte()
