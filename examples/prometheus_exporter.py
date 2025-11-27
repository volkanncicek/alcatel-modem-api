#!/usr/bin/env python3
"""
Prometheus exporter for Alcatel Modem API
Exports modem metrics in Prometheus format for monitoring

Based on: https://github.com/.../nos-modem-alcatel-mw40v-prometheus-exporther
"""

import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from alcatel_modem_api import AlcatelModemAPI


class PrometheusExporter:
    """Prometheus metrics exporter for Alcatel modems"""

    def __init__(self, api: AlcatelModemAPI, update_interval: int = 10):
        """
        Initialize exporter

        Args:
            api: AlcatelModemAPI instance
            update_interval: Update interval in seconds (default: 10)
        """
        self.api = api
        self.update_interval = update_interval
        self.metrics = {}
        self.last_update = 0

    def collect_metrics(self):
        """Collect metrics from modem"""
        try:
            # Get system info (once, doesn't change often)
            system_info = self.api.get_system_info()
            imei = system_info.get("IMEI", "unknown")
            imsi = system_info.get("IMSI", "unknown")
            mac_address = system_info.get("MacAddress", "unknown").strip()

            # Get system status
            system_status = self.api.get_system_status()

            # Get network info (requires login) - for detailed signal metrics
            try:
                network_info = self.api.get_network_info()
            except Exception:
                network_info = {}

            # Get connection state (requires login)
            try:
                connection_state = self.api.get_connection_state()
            except Exception:
                connection_state = {}

            # Get SMS storage state (public command, no login needed)
            try:
                sms_storage = self.api.get_sms_storage_state()
            except Exception as e:
                # Log error but continue
                print(f"Warning: Could not get SMS storage state: {e}", file=sys.stderr)
                sms_storage = {}

            # Build metrics
            labels = f'imei="{imei}",imsi="{imsi}",mac_address="{mac_address}"'

            metrics = []

            # System Status Metrics
            metrics.append(f'battery_capacity_percent{{{labels}}} {system_status.get("bat_cap", 0)}')
            metrics.append(f'battery_level{{{labels}}} {system_status.get("bat_level", 0)}')
            metrics.append(f'current_connection_count{{{labels}}} {system_status.get("curr_num", 0)}')
            metrics.append(f'total_connection_count{{{labels}}} {system_status.get("TotalConnNum", 0)}')
            metrics.append(f'signal_strength{{{labels}}} {system_status.get("SignalStrength", 0)}')
            metrics.append(f'roaming{{{labels}}} {system_status.get("Roaming", 0)}')
            metrics.append(f'domestic_roaming{{{labels}}} {system_status.get("Domestic_Roaming", 0)}')
            metrics.append(f'network_type{{{labels}}} {system_status.get("NetworkType", 0)}')

            # Network Info Metrics (detailed signal info)
            if network_info:
                # Signal quality metrics (from Munin plugin)
                if network_info.get("SINR"):
                    metrics.append(f'sinr{{{labels}}} {int(network_info.get("SINR", -999))}')
                if network_info.get("RSRP"):
                    metrics.append(f'rsrp{{{labels}}} {int(network_info.get("RSRP", -999))}')
                if network_info.get("RSSI"):
                    metrics.append(f'rssi{{{labels}}} {int(network_info.get("RSSI", -999))}')
                if network_info.get("RSRQ"):
                    metrics.append(f'rsrq{{{labels}}} {int(network_info.get("RSRQ", -999))}')
                if network_info.get("EcIo"):
                    metrics.append(f'ecio{{{labels}}} {float(network_info.get("EcIo", 0))}')
                if network_info.get("RSCP"):
                    metrics.append(f'rscp{{{labels}}} {int(network_info.get("RSCP", -999))}')
                if network_info.get("CellId"):
                    metrics.append(f'cell_id{{{labels}}} {network_info.get("CellId", 0)}')
                if network_info.get("eNBID"):
                    metrics.append(f'enb_id{{{labels}}} {network_info.get("eNBID", 0)}')

            # Connection State Metrics
            if connection_state:
                metrics.append(f'connection_status{{{labels}}} {connection_state.get("ConnectionStatus", 0)}')
                metrics.append(f'speed_download{{{labels}}} {connection_state.get("Speed_Dl", 0)}')
                metrics.append(f'speed_upload{{{labels}}} {connection_state.get("Speed_Ul", 0)}')
                metrics.append(f'download_rate{{{labels}}} {connection_state.get("DlRate", 0)}')
                metrics.append(f'upload_rate{{{labels}}} {connection_state.get("UlRate", 0)}')
                metrics.append(f'download_bytes{{{labels}}} {connection_state.get("DlBytes", 0)}')
                metrics.append(f'upload_bytes{{{labels}}} {connection_state.get("UlBytes", 0)}')
                metrics.append(f'connection_time{{{labels}}} {connection_state.get("ConnectionTime", 0)}')

            # SMS Metrics
            if sms_storage:
                metrics.append(f'unread_sms_count{{{labels}}} {sms_storage.get("UnreadSMSCount", 0)}')
                metrics.append(f'sms_left_count{{{labels}}} {sms_storage.get("LeftCount", 0)}')
                metrics.append(f'sms_max_count{{{labels}}} {sms_storage.get("MaxCount", 0)}')
                metrics.append(f'sms_total_used{{{labels}}} {sms_storage.get("TUseCount", 0)}')

            self.metrics = metrics
            self.last_update = time.time()

        except Exception as e:
            print(f"Error collecting metrics: {e}", file=sys.stderr)
            self.metrics = [f'# Error collecting metrics: {e}']

    def get_metrics(self) -> str:
        """Get metrics in Prometheus format"""
        current_time = time.time()

        # Update metrics if needed
        if current_time - self.last_update >= self.update_interval:
            self.collect_metrics()

        return '\n'.join(self.metrics) + '\n'


class MetricsHandler(BaseHTTPRequestHandler):
    """HTTP handler for Prometheus metrics endpoint"""

    def __init__(self, exporter, *args, **kwargs):
        self.exporter = exporter
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/metrics':
            metrics = self.exporter.get_metrics()
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; version=0.0.4')
            self.end_headers()
            self.wfile.write(metrics.encode('utf-8'))
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            html = """
            <html>
            <head><title>Alcatel Modem Prometheus Exporter</title></head>
            <body>
            <h1>Alcatel Modem Prometheus Exporter</h1>
            <p><a href="/metrics">Metrics</a></p>
            </body>
            </html>
            """
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


def create_handler(exporter):
    """Create handler with exporter"""
    def handler(*args, **kwargs):
        MetricsHandler(exporter, *args, **kwargs)
    return handler


def main():
    import argparse
    import os

    parser = argparse.ArgumentParser(description="Prometheus exporter for Alcatel Modem")
    parser.add_argument("-u", "--url", default=os.getenv("MODEM_URL", "http://192.168.1.1"),
                       help="Modem URL (default: http://192.168.1.1 or MODEM_URL env)")
    parser.add_argument("-p", "--password", default=os.getenv("MODEM_PASSWORD"),
                       help="Admin password (or MODEM_PASSWORD env)")
    parser.add_argument("--port", type=int, default=int(os.getenv("EXPORTER_PORT", "8080")),
                       help="Exporter port (default: 8080 or EXPORTER_PORT env)")
    parser.add_argument("--interval", type=int, default=int(os.getenv("UPDATE_INTERVAL", "10")),
                       help="Update interval in seconds (default: 10 or UPDATE_INTERVAL env)")
    parser.add_argument("--log-level", default=os.getenv("LOG_LEVEL", "INFO").upper(),
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Log level (default: INFO or LOG_LEVEL env)")

    args = parser.parse_args()

    # Initialize API
    api = AlcatelModemAPI(args.url, args.password)

    # Initialize exporter
    exporter = PrometheusExporter(api, args.interval)

    # Initial metrics collection
    print(f"Collecting initial metrics from {args.url}...")
    exporter.collect_metrics()
    print("✅ Initial metrics collected")

    # Start HTTP server
    handler = create_handler(exporter)
    httpd = HTTPServer(('', args.port), handler)

    print(f"🚀 Prometheus exporter started on port {args.port}")
    print(f"📊 Metrics available at: http://localhost:{args.port}/metrics")
    print(f"⏱️  Update interval: {args.interval} seconds")
    print("\nPress Ctrl+C to stop...")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Stopping exporter...")
        httpd.shutdown()


if __name__ == "__main__":
    main()

