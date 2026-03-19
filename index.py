import pandas as pd
import requests
import io
from datetime import datetime

# URL de SharePoint
URL_DATA = "https://manpowergroupcolombia-my.sharepoint.com/:x:/g/personal/edwar_vanegas_manpowercolombia_com/IQCFVQXe44GSZglu9VIZ2dGAS0h1seOoV-hJ812-oW8tys?e=o0J3Aa&download=1"

def generar_reporte():
    try:
        print("Descargando datos...")
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(URL_DATA, headers=headers, timeout=30)
        r.raise_for_status()

        # 1. Leer datos (MES como texto)
        df = pd.read_csv(io.BytesIO(r.content), sep=';', encoding='latin1', dtype={'MES': str})
        
        # 2. Filtro de fecha: Solo mostrar lo que es menor o igual a HOY
        df['Fecha_DT'] = pd.to_datetime(df['Fecha'], errors='coerce')
        hoy = datetime.now()
        df = df[df['Fecha_DT'] <= hoy].copy()
        
        # 3. Aplicar reglas: -1 es ✔️ | Vacío es ❌
        df = df.fillna('❌')
        df = df.replace(['-1', '-1.0', -1], '✔️')
        
        # Limpieza
        df = df.sort_values(by='Fecha_DT', ascending=False)
        df = df.drop(columns=['Fecha_DT'])

        # 4. Diseño HTML (Lo que se verá en la web)
        html_content = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Reporte de Gestión</title>
            <style>
                body {{ font-family: sans-serif; background: #f4f7f9; padding: 20px; }}
                .card {{ background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); max-width: 1200px; margin: auto; }}
                .filtros {{ display: flex; gap: 10px; margin-bottom: 20px; background: #eee; padding: 15px; border-radius: 8px; }}
                input {{ padding: 10px; border: 1px solid #ccc; border-radius: 5px; flex: 1; }}
                button {{ padding: 10px 20px; background: #002d5a; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
                th {{ background: #002d5a; color: white; padding: 12px; font-size: 13px; }}
                td {{ padding: 10px; border-bottom: 1px solid #eee; font-size: 12px; }}
                .v {{ color: green; font-weight: bold; }}
                .x {{ color: red; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h2>📊 Reporte Operativo (Lunes a Sábado)</h2>
                <div class="filtros">
                    <input type="text" id="buscNombre" placeholder="Buscar por Nombre Completo...">
                    <button onclick="filtrar()">🔍 BUSCAR</button>
                </div>
                <div style="overflow-x:auto;">
                    {df.to_html(index=False, table_id="miTabla", classes="display")}
                </div>
            </div>
            <script>
                function filtrar() {{
                    const tabla = document.getElementById("miTabla");
                    const nom = document.getElementById("buscNombre").value.toUpperCase();
                    const filas = tabla.getElementsByTagName("tr");
                    for (let i = 1; i < filas.length; i++) {{
                        const tdNom = filas[i].cells[4] ? filas[i].cells[4].innerText.toUpperCase() : "";
                        filas[i].style.display = tdNom.includes(nom) ? "" : "none";
                    }}
                }}
            </script>
        </body>
        </html>
        """
        
        # Colorear iconos
        html_content = html_content.replace('✔️', '<span class="v">✔️</span>').replace('❌', '<span class="x">❌</span>')

        # ESTA LÍNEA ES LA QUE CREA EL ARCHIVO FISICAMENTE
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print("✅ index.html generado con éxito.")

    except Exception as e:
        print(f"❌ Error en Python: {e}")

if __name__ == "__main__":
    generar_reporte()
