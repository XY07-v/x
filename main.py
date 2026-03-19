import pandas as pd
import requests
import io

URL = "https://manpowergroupcolombia-my.sharepoint.com/:x:/g/personal/edwar_vanegas_manpowercolombia_com/IQCFQVQEx44GSZgIu9VIZ2dGAS0h1sEo0V-hJ812-oW8tys?e=o0J3Aa&download=1"

def generar_reporte_nestle():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(URL, headers=headers, timeout=30)
        # Leer con latin1 para evitar errores de eñes o tildes
        df = pd.read_csv(io.BytesIO(response.content), sep=';', dtype=str, encoding='latin1')
        
        # 1. Limpieza de nombres de columnas
        df.columns = df.columns.str.replace('ï»¿', '') # Limpiar caracteres raros
        
        # 2. Aplicar tus reglas de negocio (Chulos y Equis)
        # Asumiendo que las columnas de cumplimiento se llaman 'L. Inicial', 'L. Final' o similares
        for col in df.columns:
            df[col] = df[col].replace(['nan', 'None', '', 'nan.1'], '<span style="color: #dc3545; font-weight: bold;">X</span>')
            df[col] = df[col].replace(['-1', '-1.0'], '<span style="color: #28a745; font-weight: bold;">✓</span>')

        html_table = df.to_html(classes='display nowrap', index=False, escape=False, table_id="tablaReporte")

        # 3. HTML con Filtros Select e Inteligencia
        html_final = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Nestlé Professional - Reporte de Logueo</title>
            <link rel="stylesheet" href="https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css">
            <style>
                body {{ font-family: 'Segoe UI', Arial; margin: 0; background-color: #f4f4f4; }}
                .header-nestle {{ background: #1a2c4e; color: white; padding: 20px; text-align: center; border-bottom: 4px solid #cc0000; }}
                .container {{ width: 98%; margin: 15px auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                
                /* Estilo Filtros */
                .filtros-box {{ display: flex; gap: 15px; flex-wrap: wrap; background: #eee; padding: 15px; border-radius: 8px; margin-bottom: 20px; align-items: flex-end; }}
                .filtro-group {{ display: flex; flex-direction: column; gap: 5px; flex: 1; min-width: 180px; }}
                .filtro-group label {{ font-weight: bold; font-size: 12px; color: #333; }}
                select {{ padding: 8px; border-radius: 4px; border: 1px solid #ccc; background: white; }}
                
                .btn-aplicar {{ background: #cc0000; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; font-weight: bold; height: 38px; }}
                .btn-aplicar:hover {{ background: #a00000; }}

                /* Tabla */
                table.dataTable thead th {{ background-color: #1a2c4e !important; color: white !important; font-size: 13px; }}
                .dataTables_wrapper {{ overflow-x: hidden !important; }}
            </style>
        </head>
        <body>
            <div class="header-nestle">
                <h1>NESTLÉ PROFESSIONAL</h1>
                <p>Reporte de Control de Logueos y Deslogueos (Lun-Sáb)</p>
            </div>

            <div class="container">
                <div class="filtros-box">
                    <div class="filtro-group">
                        <label>FECHA</label>
                        <select id="selFecha"><option value="">Todas</option></select>
                    </div>
                    <div class="filtro-group">
                        <label>NOMBRE COMPLETO</label>
                        <select id="selNombre"><option value="">Todos</option></select>
                    </div>
                    <div class="filtro-group">
                        <label>REGIONAL</label>
                        <select id="selRegional"><option value="">Todas</option></select>
                    </div>
                    <div class="filtro-group">
                        <label>NOTA</label>
                        <select id="selNota"><option value="">Todas</option></select>
                    </div>
                    <button class="btn-aplicar" onclick="aplicarFiltros()">APLICAR FILTROS</button>
                </div>

                {html_table}
            </div>

            <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
            <script src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>
            
            <script>
                $(document).ready(function() {{
                    var table = $('#tablaReporte').DataTable({{
                        "pageLength": 50,
                        "responsive": true,
                        "dom": 'rtip',
                        "language": {{ "url": "//cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json" }}
                    }});

                    // Función para llenar los SELECT con valores ÚNICOS
                    function llenarSelect(colIndex, selectId) {{
                        table.column(colIndex).data().unique().sort().each(function(d, j) {{
                            // Limpiar HTML si existe en el dato
                            var texto = d.replace(/<[^>]*>?/gm, '');
                            if(texto.trim() != "") {{
                                $(selectId).append('<option value="'+texto+'">'+texto+'</option>');
                            }}
                        }});
                    }}

                    // Llenar los desplegables (Ajustar índices de columna si es necesario)
                    llenarSelect(0, '#selFecha');    // Columna 0
                    llenarSelect(1, '#selNombre');   // Columna 1
                    llenarSelect(3, '#selRegional'); // Columna 3 (Ajustar según tu Excel)
                    
                    // Buscar columna NOTA dinámicamente
                    var idxNota = -1;
                    $('#tablaReporte thead th').each(function(i) {{
                        if($(this).text().toUpperCase().includes('NOTA')) idxNota = i;
                    }});
                    if(idxNota != -1) llenarSelect(idxNota, '#selNota');

                    // Función del Botón
                    window.aplicarFiltros = function() {{
                        table.column(0).search($('#selFecha').val());
                        table.column(1).search($('#selNombre').val());
                        table.column(3).search($('#selRegional').val());
                        if(idxNota != -1) table.column(idxNota).search($('#selNota').val());
                        table.draw();
                    }};
                }});
            </script>
        </body>
        </html>
        """
        
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_final)
        print("Reporte Nestlé generado con filtros desplegables.")

    except Exception as e:
        print(f"Error: {{e}}")

if __name__ == "__main__":
    generar_reporte_nestle()
