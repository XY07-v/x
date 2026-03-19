import pandas as pd
import requests
import io
import os
from datetime import datetime

# Configuración de la fuente de datos
URL_DATA = "https://manpowergroupcolombia-my.sharepoint.com/:x:/g/personal/edwar_vanegas_manpowercolombia_com/IQCFVQXe44GSZglu9VIZ2dGAS0h1seOoV-hJ812-oW8tys?e=o0J3Aa&download=1"

def generar_reporte_completo():
    try:
        print("--- 1. Descargando datos desde SharePoint ---")
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(URL_DATA, headers=headers, timeout=30)
        response.raise_for_status()

        # 2. Leer datos (MES como texto y delimitador ;)
        # Usamos latin1 para evitar errores de tildes comunes en archivos de Excel/CSV regionales
        df = pd.read_csv(io.BytesIO(response.content), sep=';', dtype={'MES': str}, encoding='latin1')
        
        if df.empty:
            print("⚠️ El archivo está vacío.")
            return

        # 3. Aplicar reglas de negocio personalizadas
        # -1 es positivo (✔️) | Vacío es déficit (❌)
        df = df.astype(str)
        df = df.replace(['nan', 'None', '', 'nan.1'], '❌')
        df = df.replace(['-1', '-1.0'], '✔️')

        # 4. Diseño Visual (CSS Moderno)
        estilo_css = """
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f9; color: #333; margin: 20px; }
            .container { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            h2 { color: #0056b3; border-bottom: 2px solid #0056b3; padding-bottom: 10px; }
            .info-box { background: #e9ecef; padding: 10px; border-radius: 5px; margin-bottom: 20px; font-size: 0.9em; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px; }
            th { background-color: #002d5a; color: white; padding: 12px; text-align: left; }
            td { padding: 10px; border-bottom: 1px solid #ddd; }
            tr:hover { background-color: #f1f1f1; }
            .pos { color: #28a745; font-weight: bold; }
            .neg { color: #dc3545; font-weight: bold; }
        </style>
        """

        # 5. Generar Tabla HTML
        html_table = df.to_html(classes='table', index=False, escape=False)
        
        # Inyección de colores inteligentes para los iconos
        html_table = html_table.replace('✔️', '<span class="pos">✔️</span>')
        html_table = html_table.replace('❌', '<span class="neg">❌</span>')

        # 6. Construcción del documento final (HTML completo)
        fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        html_final = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Reporte de Gestión</title>
            {estilo_css}
        </head>
        <body>
            <div class="container">
                <h2>📊 Reporte de Gestión: Lunes a Sábado</h2>
                <div class="info-box">
                    <strong>Reglas:</strong> -1 = ✔️ (Positivo) | Vacío = ❌ (Déficit)<br>
                    <strong>Nota:</strong> Los domingos y festivos no se contabilizan.<br>
                    <strong>Última actualización:</strong> {fecha_actual}
                </div>
                {html_table}
            </div>
        </body>
        </html>
        """

        # 7. Guardar el archivo
        file_name = "index.html"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(html_final)
            
        print(f"\n✅ Archivo '{file_name}' generado con éxito total.")

    except Exception as e:
        print(f"❌ Error crítico: {e}")

if __name__ == "__main__":
    generar_reporte_completo()
