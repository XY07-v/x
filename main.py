import pandas as pd
import requests
import io
from datetime import datetime

# Configuración de origen
URL_DATA = "https://manpowergroupcolombia-my.sharepoint.com/:x:/g/personal/edwar_vanegas_manpowercolombia_com/IQCFVQXe44GSZglu9VIZ2dGAS0h1seOoV-hJ812-oW8tys?e=o0J3Aa&download=1"

def ejecutar_todo():
    try:
        # 1. Descarga
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(URL_DATA, headers=headers, timeout=30)
        
        # 2. Procesamiento (MES como texto y Filtro Fecha <= Hoy)
        df = pd.read_csv(io.BytesIO(r.content), sep=';', encoding='latin1', dtype={'MES': str})
        df['Fecha_DT'] = pd.to_datetime(df['Fecha'], errors='coerce')
        df = df[df['Fecha_DT'] <= datetime.now()].copy()
        
        # 3. Reglas de iconos: -1 es ✔️, vacío es ❌
        df = df.fillna('❌')
        df = df.replace(['-1', '-1.0', -1], '✔️')
        df = df.drop(columns=['Fecha_DT'])

        # 4. Generación del HTML (El "Index" dentro del "Main")
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Reporte Unificado</title>
            <style>
                body {{ font-family: sans-serif; margin: 20px; background: #f0f2f5; }}
                .card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                table {{ width: 100%; border-collapse: collapse; display: none; }}
                th {{ background: #002d5a; color: white; padding: 10px; }}
                td {{ padding: 8px; border-bottom: 1px solid #ddd; }}
                .v {{ color: green; font-weight: bold; }}
                .x {{ color: red; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h2>📊 Reporte de Gestión Manpower</h2>
                <input type="text" id="busc" placeholder="Nombre del empleado...">
                <button onclick="buscar()">🔍 BUSCAR</button>
                <div style="margin-top:20px">
                    {df.to_html(index=False, table_id="tabla", border=0)}
                </div>
            </div>
            <script>
                function buscar() {{
                    const t = document.getElementById("tabla");
                    const fil = document.getElementById("busc").value.toUpperCase();
                    const rows = t.getElementsByTagName("tr");
                    t.style.display = "table";
                    for (let i = 1; i < rows.length; i++) {{
                        const txt = rows[i].cells[4].innerText.toUpperCase();
                        rows[i].style.display = txt.includes(fil) ? "" : "none";
                    }}
                }}
            </script>
        </body>
        </html>
        """
        
        # Inyectar clases CSS a los iconos
        html_content = html_content.replace('✔️', '<span class="v">✔️</span>').replace('❌', '<span class="x">❌</span>')

        # Escribir el archivo final
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("¡index.html generado exitosamente desde main.py!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    ejecutar_todo()
