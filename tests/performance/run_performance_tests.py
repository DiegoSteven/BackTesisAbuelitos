"""
Generador de Informe de Pruebas de Rendimiento
Ejecuta las pruebas de Locust y genera un informe HTML personalizado estilo Tesis.

Uso:
    python tests/performance/run_performance_tests.py
"""

import subprocess
import csv
import os
from datetime import datetime
import json

# Configuracion
LOCUST_FILE = "tests/performance/locustfile.py"
HOST = "http://localhost:5000"
USERS = 10
SPAWN_RATE = 2
DURATION = "30s"
CSV_PREFIX = "tests/performance/results"
OUTPUT_HTML = "tests/performance/informe_rendimiento.html"


def run_locust_tests():
    """Ejecuta las pruebas de Locust"""
    print("Ejecutando pruebas de rendimiento...")
    cmd = [
        "python", "-m", "locust",
        "-f", LOCUST_FILE,
        "--host", HOST,
        "--headless",
        "-u", str(USERS),
        "-r", str(SPAWN_RATE),
        "-t", DURATION,
        f"--csv={CSV_PREFIX}"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print("Pruebas completadas!")
    return True


def read_csv_results():
    """Lee los resultados del CSV generado por Locust"""
    stats_file = f"{CSV_PREFIX}_stats.csv"
    history_file = f"{CSV_PREFIX}_stats_history.csv"
    
    if not os.path.exists(stats_file):
        print(f"Error: No se encontro {stats_file}")
        return None
    
    # Leer estadisticas finales
    endpoints = []
    aggregated = None
    with open(stats_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Name'] == 'Aggregated':
                aggregated = row
            elif row['Name']:
                endpoints.append(row)
    
    # Leer historial para graficas
    history_data = {
        'timestamp': [],
        'users': [],
        'rps': [],
        'failures': [],
        'median_response_time': [],
        'p95_response_time': []
    }
    
    if os.path.exists(history_file):
        with open(history_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            start_time = 0
            for i, row in enumerate(reader):
                ts = int(row['Timestamp'])
                if i == 0: start_time = ts
                
                # Convertir timestamp a segundos relativos (0s, 1s, 2s...)
                elapsed = ts - start_time
                history_data['timestamp'].append(f"{elapsed}s")
                history_data['users'].append(int(row['User Count']))
                
                def safe_float(val):
                    try:
                        return float(val)
                    except (ValueError, TypeError):
                        return 0.0

                history_data['rps'].append(safe_float(row['Requests/s']))
                history_data['failures'].append(safe_float(row['Failures/s']))
                history_data['median_response_time'].append(safe_float(row['50%']))
                history_data['p95_response_time'].append(safe_float(row['95%']))

    return {
        'endpoints': endpoints, 
        'aggregated': aggregated,
        'history': history_data
    }


def generate_html_report(data):
    """Genera el informe HTML con los datos"""
    
    agg = data['aggregated']
    endpoints = data['endpoints']
    history = data['history']
    
    # Calcular estadisticas
    total_requests = int(agg['Request Count'])
    total_failures = int(agg['Failure Count'])
    avg_time = float(agg['Average Response Time'])
    
    # Generar filas de la tabla
    table_rows = ""
    
    for ep in endpoints:
        method = ep['Type']
        name = ep['Name']
        requests = ep['Request Count']
        avg = float(ep['Average Response Time'])
        min_val = float(ep['Min Response Time'])
        max_val = float(ep['Max Response Time'])
        rps = float(ep['Requests/s'])
        
        method_class = "get" if method == "GET" else "post"
        
        table_rows += f"""
                    <tr>
                        <td style="text-align:center"><span class="method {method_class}">{method}</span></td>
                        <td class="endpoint">{name}</td>
                        <td style="text-align:right">{requests}</td>
                        <td style="text-align:right">{avg:,.0f} ms</td>
                        <td style="text-align:right">{min_val:,.0f} ms</td>
                        <td style="text-align:right">{max_val:,.0f} ms</td>
                        <td style="text-align:right">{rps:.2f}</td>
                    </tr>"""
    
    fecha = datetime.now().strftime("%Y-%m-%d")
    
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Informe de Rendimiento</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --text-primary: #333;
            --text-secondary: #666;
            --border-color: #ddd;
            --bg-body: #fff;
            --bg-panel: #fff;
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Segoe UI', system-ui, sans-serif;
            background-color: var(--bg-body);
            color: var(--text-primary);
            padding: 20px;
            font-size: 12px; /* Fuente pequeña solicitada */
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        h1 {{ font-size: 1.4rem; margin-bottom: 5px; color: #222; }}
        h2 {{ font-size: 1rem; margin-bottom: 10px; color: #444; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
        
        /* KPI Table */
        .kpi-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            border: 1px solid var(--border-color);
        }}
        
        .kpi-table th {{
            background-color: #f8f9fa;
            padding: 8px;
            text-align: center;
            font-weight: 600;
            color: var(--text-secondary);
            border-right: 1px solid var(--border-color);
            font-size: 11px;
            text-transform: uppercase;
        }}
        
        .kpi-table td {{
            padding: 10px;
            text-align: center;
            font-size: 1.2rem;
            font-weight: bold;
            border-right: 1px solid var(--border-color);
        }}
        
        .val-green {{ color: #10b981; }}
        .val-blue {{ color: #3b82f6; }}
        .val-orange {{ color: #f59e0b; }}
        .val-red {{ color: #ef4444; }}
        
        /* Charts Grid */
        .charts-container {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .chart-box {{
            border: 1px solid var(--border-color);
            padding: 10px;
            border-radius: 4px;
            height: 250px;
        }}
        
        /* Data Table */
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 11px;
        }}
        
        .data-table th {{
            background-color: #f8f9fa;
            padding: 6px 8px;
            text-align: left;
            border-bottom: 2px solid var(--border-color);
            color: #444;
        }}
        
        .data-table td {{
            padding: 6px 8px;
            border-bottom: 1px solid #eee;
        }}
        
        .endpoint {{ font-family: monospace; color: #444; }}
        
        .method {{
            font-size: 9px;
            padding: 2px 4px;
            border-radius: 3px;
            font-weight: bold;
            color: #fff;
        }}
        
        .method.get {{ background-color: #10b981; }}
        .method.post {{ background-color: #f59e0b; }}
        
        .footer {{
            margin-top: 20px;
            text-align: center;
            color: #999;
            font-size: 10px;
            border-top: 1px solid #eee;
            padding-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div style="margin-bottom: 15px;">
            <h1>Informe de Rendimiento</h1>
            <div style="color: #666; font-size: 11px;">Fecha: {fecha} | Herramienta: Locust | Duracion: {DURATION}</div>
        </div>
        
        <!-- KPI Table Compacta -->
        <table class="kpi-table">
            <thead>
                <tr>
                    <th>Total Requests</th>
                    <th>Tiempo Promedio</th>
                    <th>Usuarios Concurrentes</th>
                    <th>Tasa de Error</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="val-green">{total_requests}</td>
                    <td class="val-blue">{avg_time/1000:.2f}s</td>
                    <td class="val-orange">{USERS}</td>
                    <td class="{ 'val-red' if total_failures > 0 else 'val-green' }">{total_failures}</td>
                </tr>
            </tbody>
        </table>
        
        <!-- Graficas -->
        <div class="charts-container">
            <div class="chart-box">
                <h2>Rendimiento (Requests/seg)</h2>
                <div style="height: 200px; width: 100%;">
                    <canvas id="rpsChart"></canvas>
                </div>
            </div>
            <div class="chart-box">
                <h2>Latencia y Tiempo de Respuesta</h2>
                <div style="height: 200px; width: 100%;">
                    <canvas id="responseTimeChart"></canvas>
                </div>
            </div>
        </div>
        
        <!-- Tabla Detallada -->
        <h2>Detalle por Endpoint</h2>
        <table class="data-table">
            <thead>
                <tr>
                    <th style="width: 50px; text-align:center">Metodo</th>
                    <th>Endpoint</th>
                    <th style="text-align:right">Requests</th>
                    <th style="text-align:right">Promedio</th>
                    <th style="text-align:right">Min</th>
                    <th style="text-align:right">Max</th>
                    <th style="text-align:right">Req/s</th>
                </tr>
            </thead>
            <tbody>{table_rows}
            </tbody>
        </table>
        
        <div class="footer">
            Generado automaticamente por script de pruebas.
        </div>
    </div>

    <script>
        Chart.defaults.font.size = 10;
        Chart.defaults.color = '#666';
        
        const historyData = {json.dumps(history)};
        
        // RPS Chart
        new Chart(document.getElementById('rpsChart'), {{
            type: 'line',
            data: {{
                labels: historyData.timestamp,
                datasets: [
                    {{
                        label: 'Requests/s',
                        data: historyData.rps,
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.3,
                        pointRadius: 0
                    }},
                    {{
                        label: 'Errores/s',
                        data: historyData.failures,
                        borderColor: '#ef4444',
                        borderWidth: 2,
                        fill: false,
                        tension: 0.3,
                        pointRadius: 0
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'bottom', labels: {{ boxWidth: 10 }} }}
                }},
                scales: {{
                    y: {{ beginAtZero: true, grid: {{ color: '#f0f0f0' }} }},
                    x: {{ grid: {{ display: false }}, ticks: {{ maxTicksLimit: 8 }} }}
                }}
            }}
        }});
        
        // Response Time Chart
        new Chart(document.getElementById('responseTimeChart'), {{
            type: 'line',
            data: {{
                labels: historyData.timestamp,
                datasets: [
                    {{
                        label: 'Mediana (P50)',
                        data: historyData.median_response_time,
                        borderColor: '#3b82f6',
                        borderWidth: 2,
                        tension: 0.3,
                        pointRadius: 0
                    }},
                    {{
                        label: 'P95 (Latencia Alta)',
                        data: historyData.p95_response_time,
                        borderColor: '#f59e0b',
                        borderWidth: 2,
                        borderDash: [5, 5],
                        tension: 0.3,
                        pointRadius: 0
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'bottom', labels: {{ boxWidth: 10 }} }}
                }},
                scales: {{
                    y: {{ beginAtZero: true, grid: {{ color: '#f0f0f0' }} }},
                    x: {{ grid: {{ display: false }}, ticks: {{ maxTicksLimit: 8 }} }}
                }}
            }}
        }});
    </script>
</body>
</html>"""
    
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Informe generado: {OUTPUT_HTML}")


def main():
    print("=" * 60)
    print("GENERADOR DE INFORME - SIN EJECUTAR PRUEBAS")
    print("=" * 60)
    
    # Leer resultados existentes
    data = read_csv_results()
    if not data:
        print("Error leyendo resultados.")
        return
    
    # Generar informe
    generate_html_report(data)
    
    print("=" * 60)
    print("COMPLETADO!")
    print(f"Abrir: {OUTPUT_HTML}")
    print("=" * 60)


if __name__ == "__main__":
    main()
