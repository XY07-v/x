import pandas as pd
import requests
import io
from datetime import datetime

# URL de descarga directa
URL_DATA = "https://manpowergroupcolombia-my.sharepoint.com/:x:/g/personal/edwar_vanegas_manpowercolombia_com/IQCFVQXe44GSZglu9VIZ2dGAS0h1seOoV-hJ812-oW8tys?e=o0J3Aa&download=1"

def generar_reporte_pro():
    try:
        print("--- Iniciando descarga de datos ---")
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(URL_DATA, headers=headers, timeout=30)
        r.raise_for_status()

        # 1. Carga de datos
        df = pd.read_csv(io.BytesIO(r.content), sep=';', encoding='latin1')
        
        # 2. Convertir fechas y filtrar (solo <= hoy)
        # Intentamos detectar el formato de fecha (día/mes/año o año-mes-día)
        df['Fecha_Clean'] = pd.to_datetime(df['Fecha'], errors='coerce')
        hoy = datetime.now()
        df = df[df['Fecha_Clean'] <= hoy].copy()
        
        # 3. Limpieza y Reglas de Negocio
        # -1 -> ✔️ | Vacío -> ❌
        df = df.fillna('❌')
        df = df.replace(['-1', '-1.0', -1], '✔️')
        
        # Ordenar por fecha más reciente arriba
        df = df.sort_values(by='Fecha_Clean', ascending=False)
        df = df.drop(columns=['Fecha_Clean'])

        # 4. Estructura HTML con Buscador y CSS
        html_content = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reporte de Gestión Manpower</title>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #f8f9fa; margin: 0; padding: 20px; }}
                .container {{ max-width: 1200px; margin: auto; background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
                header {{ text-align: center; border-bottom: 3px solid #002d5a; margin-bottom: 20px; padding-bottom: 10px; }}
                .search-panel {{ background: #eef2f7; padding: 20px; border-radius: 8px; margin-bottom: 20px; display: flex; gap: 15px; flex-wrap: wrap; align-items: flex-end; }}
                .input-group {{ display: flex; flex-direction: column; gap: 5px; }}
                input {{ padding: 10px; border: 1px solid #ccc; border-radius: 5px; min-width: 200px; }}
                button {{ background-color: #002d5a; color: white; padding: 10px 25px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; transition: 0.3s; }}
                button:hover {{ background-color: #004a99; transform: translateY(-2px); }}
                .table-wrapper {{ overflow-x: auto; }}
                table {{ width: 100%; border-collapse: collapse; display: none; margin-top: 20px; }}
                th {{ background-color: #002d5a; color: white; padding: 12px; font-size: 14px; text-transform: uppercase; }}
                td {{ padding: 10px; border-bottom: 1px solid #eee; font-size: 13px; text-align: left; }}
                tr:hover {{ background-color: #f1f4f8; }}
                .status-pos {{ color: #28a745; font-weight: bold; font-size: 1.2em; }}
                .status-neg {{ color: #dc3545; font-weight: bold; font-size: 1.2em; }}
                .counter {{ margin-top: 10px; font-weight: bold; color: #555; }}
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>📊 Reporte de Gestión Operativa</h1>
                    <p>Datos actualizados hasta: <strong>{hoy.strftime('%d/%m/%Y %H:%M')}</strong></p>
                </header>

                <div class="search-panel">
                    <div class="input-group">
                        <label>Nombre del Empleado:</label>
                        <input type="text" id="nameSearch" placeholder="Ej: JUAN PEREZ...">
                    </div>
                    <div class="input-group">
                        <label>Regional:</label>
                        <input type="text" id="regSearch" placeholder="Ej: ANTIOQUIA...">
                    </div>
                    <button onclick="filterData()">🔍 BUSCAR / APLICAR FILTROS</button>
                </div>
                
                <div id="resultCount" class="counter"></div>

                <div class="table-wrapper">
                    {df.to_html(index=False, table_id="dataTable", classes="display")}
                </div>
            </div>

            <script>
                function filterData() {{
                    const table = document.getElementById("dataTable");
                    const nameVal = document.getElementById("nameSearch").value.toUpperCase();
                    const regVal = document.getElementById("regSearch").value.toUpperCase();
                    const rows = table.getElementsByTagName("tr");
                    let count = 0;

                    table.style.display = "table"; // Mostrar la tabla al buscar

                    for (let i = 1; i < rows.length; i++) {{
                        const tdRegional = rows[i].cells[0].textContent.toUpperCase();
                        const tdNombre = rows[i].cells[4].textContent.toUpperCase();
                        
                        if (tdNombre.includes(nameVal) && tdRegional.includes(regVal)) {{
                            rows[i].style.display = "";
                            count++;
                        }} else {{
                            rows[i].style.display = "none";
                        }}
                    }}
                    document.getElementById("resultCount").innerText = "Resultados encontrados: " + count;
                }}
            </script>
        </body>
        </html>
        """

        # Inyectar estilos para los iconos
        html_content = html_content.replace('✔️', '<span class="status-pos">✔️</span>')
        html_content = html_content.replace('❌', '<span class="status-neg">❌</span>')

        # Guardar archivo
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_content)

        print("✅ ¡Éxito! El archivo 'index.html' ha sido generado con filtros.")

    except Exception as e:
        print(f"❌ Error durante el proceso: {e}")

if __name__ == "__main__":
    generar_reporte_pro()
