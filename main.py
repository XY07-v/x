import pandas as pd
import requests
import io
import os
from datetime import datetime

# Configuración
URL_DATA = "https://manpowergroupcolombia-my.sharepoint.com/:x:/g/personal/edwar_vanegas_manpowercolombia_com/IQCFVQXe44GSZglu9VIZ2dGAS0h1seOoV-hJ812-oW8tys?e=o0J3Aa&download=1"

def generar_reporte():
    try:
        print("Descargando datos...")
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(URL_DATA, headers=headers, timeout=30)
        
        # Leer con MES como texto
        df = pd.read_csv(io.BytesIO(r.content), sep=';', encoding='latin1', dtype={'MES': str})
        
        # --- FILTRO DE FECHA (Solo <= Hoy) ---
        df['Fecha_DT'] = pd.to_datetime(df['Fecha'], errors='coerce')
        hoy = datetime.now()
        df = df[df['Fecha_DT'] <= hoy].copy()
        df = df.sort_values(by='Fecha_DT', ascending=False)
        df = df.drop(columns=['Fecha_DT'])

        # --- REGLAS DE ICONOS ---
        # -1 es positivo (✔️), vacío es déficit (❌)
        df = df.fillna('❌')
        df = df.replace(['-1', '-1.0', -1], '✔️')

        # Convertir a HTML
        tabla_html = df.to_html(index=False, table_id="tablaDatos", classes="display")

        # HTML completo con Botón Buscar y Filtros
        html_final = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Reporte de Gestión</title>
            <style>
                body {{ font-family: sans-serif; padding: 20px; background: #f4f7f9; }}
                .card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                .search-area {{ background: #e9ecef; padding: 15px; border-radius: 8px; margin-bottom: 20px; display: flex; gap: 10px; flex-wrap: wrap; }}
                input {{ padding: 8px; border: 1px solid #ccc; border-radius: 4px; }}
                button {{ padding: 8px 20px; background: #002d5a; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }}
                table {{ width: 100%; border-collapse: collapse; display: none; margin-top: 20px; }}
                th {{ background: #002d5a; color: white; padding: 10px; font-size: 12px; }}
                td {{ padding: 8px; border-bottom: 1px solid #eee; font-size: 11px; }}
                .chk {{ color: green; font-weight: bold; font-size: 1.2em; }}
                .err {{ color: red; font-weight: bold; font-size: 1.2em; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h2>📊 Reporte de Gestión Operativa</h2>
                <p>Nota: Los domingos y festivos no se contabilizan. Datos hasta hoy.</p>
                
                <div class="search-area">
                    <input type="text" id="inNombre" placeholder="Nombre del empleado...">
                    <input type="text" id="inReg" placeholder="Regional...">
                    <button onclick="buscar()">🔍 BUSCAR</button>
                </div>

                <div id="contenedor">
                    {tabla_html}
                </div>
            </div>

            <script>
                function buscar() {{
                    const tabla = document.getElementById("tablaDatos");
                    const nom = document.getElementById("inNombre").value.toUpperCase();
                    const reg = document.getElementById("inReg").value.toUpperCase();
                    const filas = tabla.getElementsByTagName("tr");

                    tabla.style.display = "table"; 

                    for (let i = 1; i < filas.length; i++) {{
                        const txtReg = filas[i].cells[0].innerText.toUpperCase();
                        const txtNom = filas[i].cells[4].innerText.toUpperCase();
                        if (txtNom.includes(nom) && txtReg.includes(reg)) {{
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
        
        # Aplicar colores a los iconos antes de guardar
        html_final = html_final.replace('✔️', '<span class="chk">✔️</span>')
        html_final = html_final.replace('❌', '<span class="err">❌</span>')

        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_final)
        print("index.html creado exitosamente.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generar_reporte()
