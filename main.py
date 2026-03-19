import pandas as pd
import requests
import io
import json

URL = "https://manpowergroupcolombia-my.sharepoint.com/:x:/g/personal/edwar_vanegas_manpowercolombia_com/IQCFQVQEx44GSZgIu9VIZ2dGAS0h1sEo0V-hJ812-oW8tys?e=o0J3Aa&download=1"

def generar_reporte_ultrarrapido():
    try:
        print("--- Descargando y Optimizando Datos ---")
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(URL, headers=headers, timeout=30)
        df = pd.read_csv(io.BytesIO(response.content), sep=';', dtype=str, encoding='latin1')
        
        # 1. Limpieza de nombres y reglas de negocio
        df.columns = df.columns.str.replace('ï»¿', '')
        for col in df.columns:
            df[col] = df[col].replace(['nan', 'None', '', 'nan.1'], 'X')
            df[col] = df[col].replace(['-1', '-1.0'], '✓')

        # 2. Extraer valores únicos para los filtros ANTES de enviar al HTML
        def get_unicos(col_name):
            if col_name in df.columns:
                return sorted(df[col_name].unique().tolist())
            return []

        filtros_data = {
            "fechas": get_unicos("Fecha"),
            "nombres": get_unicos("Nombre Completo"),
            "regionales": get_unicos("REGIONAL") if "REGIONAL" in df.columns else get_unicos(df.columns[0]),
            "notas": get_unicos("Nota") if "Nota" in df.columns else []
        }

        # 3. Convertir toda la data a un formato JSON ligero para el navegador
        data_json = df.to_json(orient='records')

        # 4. HTML con Carga Diferida (Solo renderiza al filtrar)
        html_final = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Nestlé Professional - Consulta Rápida</title>
            <link rel="stylesheet" href="https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css">
            <style>
                body {{ font-family: 'Segoe UI', Arial; margin: 0; background-color: #f0f2f5; color: #333; }}
                .header {{ background: #1a2c4e; color: white; padding: 15px; text-align: center; border-bottom: 4px solid #cc0000; }}
                .container {{ width: 98%; margin: 10px auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
                
                .filtros-box {{ display: flex; gap: 15px; flex-wrap: wrap; background: #ffffff; padding: 20px; border: 1px solid #ddd; border-radius: 8px; margin-bottom: 20px; align-items: flex-end; }}
                .filtro-item {{ display: flex; flex-direction: column; gap: 5px; flex: 1; min-width: 200px; }}
                .filtro-item label {{ font-weight: bold; font-size: 13px; color: #1a2c4e; }}
                
                select {{ padding: 10px; border-radius: 5px; border: 1px solid #bbb; background: #fff; cursor: pointer; }}
                
                .btn-consultar {{ background: #cc0000; color: white; border: none; padding: 12px 30px; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 14px; transition: 0.3s; }}
                .btn-consultar:hover {{ background: #444; transform: translateY(-2px); }}
                
                #tablaContenedor {{ display: none; margin-top: 20px; border-top: 2px solid #eee; padding-top: 20px; }}
                
                .positivo {{ color: #28a745; font-weight: bold; font-size: 1.2em; }}
                .deficit {{ color: #dc3545; font-weight: bold; font-size: 1.2em; }}
                
                table.dataTable thead th {{ background-color: #1a2c4e !important; color: white !important; padding: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2 style="margin:0;">NESTLÉ PROFESSIONAL</h2>
                <p style="margin:5px 0 0 0; font-size:14px; opacity:0.9;">Módulo de Consulta: Logueos de Personal</p>
            </div>

            <div class="container">
                <div class="filtros-box">
                    <div class="filtro-item">
                        <label>📅 FECHA</label>
                        <select id="selFecha"><option value="">-- Seleccionar Fecha --</option></select>
                    </div>
                    <div class="filtro-item">
                        <label>👤 NOMBRE COMPLETO</label>
                        <select id="selNombre"><option value="">-- Seleccionar Nombre --</option></select>
                    </div>
                    <div class="filtro-item">
                        <label>📍 REGIONAL / NOTA</label>
                        <select id="selRegional"><option value="">-- Seleccionar --</option></select>
                    </div>
                    <button class="btn-consultar" onclick="ejecutarConsulta()">🚀 CONSULTAR REPORTE</button>
                </div>

                <div id="tablaContenedor">
                    <table id="tablaReporte" class="display nowrap" style="width:100%">
                        <thead><tr id="headerRow"></tr></thead>
                        <tbody id="bodyData"></tbody>
                    </table>
                </div>
            </div>

            <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
            <script src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>

            <script>
                const fullData = {data_json};
                const filtros = {json.dumps(filtros_data)};
                let dataTableInstance = null;

                $(document).ready(function() {{
                    // Llenar selectores con únicos
                    filtros.fechas.forEach(f => $('#selFecha').append(`<option value="${{f}}">${{f}}</option>`));
                    filtros.nombres.forEach(n => $('#selNombre').append(`<option value="${{n}}">${{n}}</option>`));
                    filtros.regionales.forEach(r => $('#selRegional').append(`<option value="${{r}}">${{r}}</option>`));
                }});

                function ejecutarConsulta() {{
                    const fechaVal = $('#selFecha').val();
                    const nombreVal = $('#selNombre').val();
                    const regionalVal = $('#selRegional').val();

                    if(!fechaVal && !nombreVal && !regionalVal) {{
                        alert("Por favor selecciona al menos un filtro para optimizar la carga.");
                        return;
                    }}

                    // Filtrar la data en memoria (SUPER RÁPIDO)
                    let filtered = fullData.filter(row => {{
                        return (!fechaVal || row['Fecha'] === fechaVal) &&
                               (!nombreVal || row['Nombre Completo'] === nombreVal) &&
                               (!regionalVal || Object.values(row).includes(regionalVal));
                    }});

                    renderizarTabla(filtered);
                }}

                function renderizarTabla(data) {{
                    $('#tablaContenedor').show();
                    if (dataTableInstance) {{
                        dataTableInstance.destroy();
                        $('#headerRow').empty();
                        $('#bodyData').empty();
                    }}

                    if (data.length === 0) {{
                        alert("No se encontraron datos.");
                        return;
                    }}

                    // Crear cabeceras
                    const columns = Object.keys(data[0]);
                    columns.forEach(col => $('#headerRow').append(`<th>${{col}}</th>`));

                    // Crear filas con estilos de Chulo/Equis
                    data.forEach(row => {{
                        let tr = '<tr>';
                        columns.forEach(col => {{
                            let val = row[col];
                            if(val === '✓') val = '<span class="positivo">✓</span>';
                            if(val === 'X') val = '<span class="deficit">X</span>';
                            tr += `<td>${{val}}</td>`;
                        }});
                        tr += '</tr>';
                        $('#bodyData').append(tr);
                    }});

                    dataTableInstance = $('#tablaReporte').DataTable({{
                        "pageLength": 25,
                        "responsive": true,
                        "scrollX": false,
                        "language": {{ "url": "//cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json" }}
                    }});
                }}
            </script>
        </body>
        </html>
        """
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_final)
        print("✅ Reporte Optimizado Nestlé generado.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generar_reporte_ultrarrapido()
