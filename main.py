import pandas as pd
import requests
import io
import os

URL = "https://manpowergroupcolombia-my.sharepoint.com/:x:/g/personal/edwar_vanegas_manpowercolombia_com/IQCFQVQEx44GSZgIu9VIZ2dGAS0h1sEo0V-hJ812-oW8tys?e=o0J3Aa&download=1"

def generar_reporte_estilizado():
    try:
        print("--- Iniciando generación de reporte profesional ---")
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(URL, headers=headers, timeout=30)
        response.raise_for_status()
        
        # 1. Leer datos y renombrar columna problemática
        df = pd.read_csv(io.BytesIO(response.content), sep=';', dtype={'MES': str}, encoding='latin1')
        
        # Corrección de la columna regional (eliminar caracteres raros)
        col_regional_original = 'ï»¿REGIONAL'
        if col_regional_original in df.columns:
            df.rename(columns={col_regional_original: 'REGIONAL'}, inplace=True)
        elif 'REGIONAL' not in df.columns:
            # Si no la encuentra, asumimos que es la primera columna
            df.rename(columns={df.columns[0]: 'REGIONAL'}, inplace=True)

        # 2. Aplicar tus reglas de cumplimiento (✓ y X con colores)
        cols_cumplimiento = ['L. Inicial', 'L. Final'] # Columnas donde aplicar
        for col in cols_cumplimiento:
            if col in df.columns:
                df[col] = df[col].astype(str)
                df[col] = df[col].replace(['nan', 'None', '', 'nan.1'], '<span class="deficit">X</span>')
                df[col] = df[col].replace(['-1', '-1.0'], '<span class="positivo">✓</span>')

        # 3. Generar la estructura base de la tabla HTML (sin diseño)
        html_table = df.to_html(classes='display nowrap', index=False, escape=False, table_id="tablaReporte")

        # 4. Diseño Visual Profesional (CSS) - ¡Basado en tu imagen!
        estilo_css = """
        <style>
            body { font-family: 'Segoe UI', sans-serif; margin: 0; background-color: #f0f2f5; }
            .container { width: 95%; margin: 20px auto; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
            h2 { color: #1a2c4e; text-align: center; border-bottom: 2px solid #1a2c4e; padding-bottom: 10px; }
            
            /* TUS REGLAS DE COLOR INTERNAS */
            .positivo { color: #28a745; font-weight: bold; }
            .deficit { color: #dc3545; font-weight: bold; }

            /* ESTILOS DE LA TABLA - ¡BÚSQUEDA DEL DISEÑO DE TU IMAGEN! */
            #tablaReporte { width: 100% !important; margin-top: 10px; border-collapse: separate; border-spacing: 0; }
            #tablaReporte thead th { background-color: #1a2c4e; color: white; padding: 12px 10px; text-transform: none; font-weight: 600; font-size: 0.9em; text-align: left; }
            #tablaReporte tbody td { padding: 10px; border-bottom: 1px solid #ddd; font-size: 0.9em; color: #333; }
            #tablaReporte tbody tr:nth-child(even) { background-color: #f9f9f9; }
            #tablaReporte tbody tr:hover { background-color: #f1f4f8; }
            
            /* AJUSTE PARA QUE NO HAYA DESLIZAMIENTO LATERAL */
            .dataTables_wrapper { overflow-x: hidden !important; }
            .dataTables_scrollBody { overflow-x: hidden !important; }

            /* ESTILOS DE LOS FILTROS SUPERIORES */
            .filtros-container { display: flex; gap: 15px; margin-bottom: 20px; flex-wrap: wrap; justify-content: space-between; align-items: center; background: #fafafa; padding: 15px; border-radius: 6px; border: 1px solid #eee; }
            .filtro-item { display: flex; flex-direction: column; gap: 5px; flex-grow: 1; min-width: 250px; }
            .filtro-item label { font-size: 0.85em; font-weight: bold; color: #1a2c4e; }
            .filtro-item input, .filtro-item select { padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 0.9em; }
        </style>
        """

        # 5. Inyección de JavaScript (DataTables y Filtros Avanzados)
        js_scripts = """
        <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
        <script src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>
        <link rel="stylesheet" href="https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css">
        
        <script>
        $(document).ready(function() {
            // Inicializar DataTables
            var table = $('#tablaReporte').DataTable({
                "pageLength": 25,
                "language": { "url": "//cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json" },
                "scrollX": false, // Desactivar deslizamiento lateral
                "responsive": true, // Activar adaptabilidad
                "dom": 'lrtip', // Ocultar buscador y longitud de página por defecto
                "columnDefs": [ { "width": "150px", "targets": 1 } ] // Ajuste específico ancho nombre
            });

            // Lógica de Filtros Personalizados
            $('#filtroNombre').on('keyup change', function() { table.column(1).search(this.value).draw(); }); // Columna 1: Nombre
            $('#filtroFecha').on('keyup change', function() { table.column(0).search(this.value).draw(); });  // Columna 0: Fecha
            $('#filtroRegional').on('keyup change', function() { table.column(3).search(this.value).draw(); }); // Columna 3: Regional
        });
        </script>
        """

        # 6. Construcción del documento HTML final
        html_final = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Reporte Profesional Manpower</title>
            {estilo_css}
        </head>
        <body>
            <div class="container">
                <h2>📊 Reporte de Gestión: Lunes a Sábado</h2>
                
                <div class="filtros-container">
                    <div class="filtro-item">
                        <label>Filtrar por Fecha (DD/MM/YYYY):</label>
                        <input type="text" id="filtroFecha" placeholder="Ej: 14/03/2026">
                    </div>
                    <div class="filtro-item">
                        <label>Filtrar por Nombre Completo:</label>
                        <input type="text" id="filtroNombre" placeholder="Buscar empleado...">
                    </div>
                    <div class="filtro-item">
                        <label>Filtrar por Regional:</label>
                        <input type="text" id="filtroRegional" placeholder="Ej: ANTIOQUIA">
                    </div>
                </div>

                <hr>
                {html_table}
            </div>
            {js_scripts}
        </body>
        </html>
        """

        # Guardar archivo
        file_name = "index.html"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(html_final)
            
        print(f"\n### ✅ Reporte profesional generado con éxito: '{file_name}' ###")
        return df

    except Exception as e:
        print(f"Error crítico en el reporte: {e}")

if __name__ == "__main__":
    generar_reporte_estilizado()
