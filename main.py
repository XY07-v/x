import pandas as pd
import requests
import io

URL = "https://manpowergroupcolombia-my.sharepoint.com/:x:/g/personal/edwar_vanegas_manpowercolombia_com/IQCFQVQEx44GSZgIu9VIZ2dGAS0h1sEo0V-hJ812-oW8tys?e=o0J3Aa&download=1"

def generar_reporte_profesional():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(URL, headers=headers, timeout=30)
        df = pd.read_csv(io.BytesIO(response.content), sep=';', dtype={'MES': str}, encoding='latin1')
        
        # Limpiar nombre de columna Regional
        if 'ï»¿REGIONAL' in df.columns:
            df.rename(columns={'ï»¿REGIONAL': 'REGIONAL'}, inplace=True)

        # Aplicar tus reglas de chulos y equis con colores
        df = df.astype(str)
        for col in df.columns:
            df[col] = df[col].replace(['nan', 'None', '', 'nan.1'], '<span style="color: #dc3545; font-weight: bold;">X</span>')
            df[col] = df[col].replace(['-1', '-1.0'], '<span style="color: #28a745; font-weight: bold;">✓</span>')

        html_table = df.to_html(classes='display nowrap', index=False, escape=False, table_id="tablaReporte")

        # El nuevo index.html con FILTROS y DISEÑO DE TU IMAGEN
        html_final = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reporte Manpower</title>
            <link rel="stylesheet" href="https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css">
            <style>
                body {{ font-family: 'Segoe UI', Arial; margin: 0; background-color: #f0f2f5; }}
                .container {{ width: 98%; margin: 10px auto; background: white; padding: 15px; border-radius: 8px; }}
                h2 {{ color: #1a2c4e; text-align: center; border-bottom: 3px solid #1a2c4e; }}
                
                /* Estilo de filtros */
                .filtros {{ display: flex; gap: 10px; margin-bottom: 15px; flex-wrap: wrap; background: #f8f9fa; padding: 10px; border-radius: 5px; }}
                .filtros input {{ padding: 8px; border: 1px solid #ccc; border-radius: 4px; flex: 1; min-width: 200px; }}

                /* Estilo tabla como tu imagen */
                table.dataTable thead th {{ background-color: #1a2c4e !important; color: white !important; text-align: left; }}
                table.dataTable tbody tr:nth-child(even) {{ background-color: #f9f9f9; }}
                
                /* Evitar scroll lateral */
                .dataTables_wrapper {{ overflow-x: hidden !important; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>📊 Reporte de Gestión: Lunes a Sábado</h2>
                <div class="filtros">
                    <input type="text" id="fFecha" placeholder="Filtrar por Fecha...">
                    <input type="text" id="fNombre" placeholder="Filtrar por Nombre...">
                    <input type="text" id="fRegional" placeholder="Filtrar por Regional...">
                </div>
                {html_table}
            </div>
            <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
            <script src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>
            <script>
                $(document).ready(function() {{
                    var table = $('#tablaReporte').DataTable({{
                        "pageLength": 50,
                        "language": {{ "url": "//cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json" }},
                        "responsive": true,
                        "dom": 'rtip'
                    }});
                    // Eventos de filtros
                    $('#fFecha').on('keyup', function() {{ table.column(0).search(this.value).draw(); }});
                    $('#fNombre').on('keyup', function() {{ table.column(1).search(this.value).draw(); }});
                    $('#fRegional').on('keyup', function() {{ table.column(2).search(this.value).draw(); }});
                }});
            </script>
        </body>
        </html>
        """
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_final)
        print("index.html actualizado con éxito.")

    except Exception as e:
        print(f"Error: {{e}}")

if __name__ == "__main__":
    generar_reporte_profesional()
