import pandas as pd
import requests
import io
from datetime import datetime

# URL de descarga directa de SharePoint
URL_DATA = "https://manpowergroupcolombia-my.sharepoint.com/:x:/g/personal/edwar_vanegas_manpowercolombia_com/IQCFVQXe44GSZglu9VIZ2dGAS0h1seOoV-hJ812-oW8tys?e=o0J3Aa&download=1"

def generar_reporte():
    try:
        print("--- Iniciando proceso de datos ---")
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(URL_DATA, headers=headers, timeout=30)
        r.raise_for_status()

        # 1. Cargar datos (MES como texto)
        df = pd.read_csv(io.BytesIO(r.content), sep=';', encoding='latin1', dtype={'MES': str})
        
        # 2. Filtro de Fecha: Solo mostrar lo que es <= hoy
        df['Fecha_DT'] = pd.to_datetime(df['Fecha'], errors='coerce')
        hoy = datetime.now()
        df = df[df['Fecha_DT'] <= hoy].copy()
        
        # 3. Aplicar reglas: -1 -> ✔️ | Vacío -> ❌
        df = df.fillna('❌')
        df = df.replace(['-1', '-1.0', -1], '✔️')
        
        # Ordenar por fecha reciente y quitar columna auxiliar
        df = df.sort_values(by='Fecha_DT', ascending=False)
        df = df.drop(columns=['Fecha_DT'])

        # 4. Generar el HTML con Buscador y CSS
        html_template = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reporte de Gestión Operativa</title>
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; background-color: #f4f7f9; padding: 20px; }}
                .card {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); max-width: 1200px; margin: auto; }}
                h2 {{ color: #002d5a; text-align: center; }}
                .filtros {{ display: flex; gap: 10px; margin-bottom: 20px; background: #e9ecef; padding: 15px; border-radius: 8px; flex-wrap: wrap; }}
                input {{ padding: 10px; border: 1px solid #ccc; border-radius: 5px; flex: 1; min-width: 200px; }}
                button {{ padding: 10px 25px; background: #002d5a; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }}
                button:hover {{ background: #004080; }}
                .tabla-container {{ overflow-x: auto; }}
                table {{ width: 100%; border-collapse: collapse; display: none; margin-top: 15px; }}
                th {{ background: #002d5a; color: white; padding: 12px; font-size: 13px; text-align: left; }}
                td {{ padding: 10px; border-bottom: 1px solid #eee; font-size: 12px; }}
                .v {{ color: #28a745; font-weight: bold; }}
                .x {{ color: #dc3545; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h2>📊 Reporte de Gestión (Lunes a Sábado)</h2>
                <div class="filtros">
                    <input type="text" id="buscNombre" placeholder="Nombre completo...">
                    <input type="text" id="buscReg" placeholder="Regional...">
                    <button onclick="filtrar()">🔍 BUSCAR</button>
                </div>
                <div class="tabla-container">
                    {df.to_html(index=False, table_id="miTabla", classes="display")}
                </div>
            </div>
            <script>
                function filtrar() {{
                    const tabla = document.getElementById("miTabla");
                    const nom = document.getElementById("buscNombre").value.toUpperCase();
                    const reg = document.getElementById("buscReg").value.toUpperCase();
                    const filas = tabla.getElementsByTagName("tr");
                    
                    tabla.style.display = "table"; 

                    for (let i = 1; i < filas.length; i++) {{
                        const tdReg = filas[i].cells[0].innerText.toUpperCase();
                        const tdNom = filas[i].cells[4].innerText.toUpperCase();
                        if (tdNom.includes(nom) && tdReg.includes(reg)) {{
                            filas[i].style.display = "";
                        }} else {{
                            filas[i].style.display = "none";
                        }}
                    }}
                }}
            </script>
        </body>
        </html>
        """

        # Inyectar estilos para los iconos
        html_template = html_template.replace('✔️', '<span class="v">✔️</span>')
        html_template = html_template.replace('❌', '<span class="x">❌</span>')

        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_template)
            
        print("✅ index.html generado con éxito.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generar_reporte()
