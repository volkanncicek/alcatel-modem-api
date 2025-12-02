#!/usr/bin/env python3
"""
Prometheus exporter for Alcatel Modem API
Exports modem metrics in Prometheus format for monitoring

Based on: https://github.com/philalex/nos-modem-alcatel-mw40v-prometheus-exporther
"""

import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from alcatel_modem_api import AlcatelClient


class PrometheusExporter:
    """Prometheus metrics exporter for Alcatel modems"""

    def __init__(self, api: AlcatelClient, update_interval: int = 10):
        """
        Initialize exporter

        Args:
            api: AlcatelClient instance
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
            system_info = self.api.system.get_info()
            imei = system_info.get("IMEI", "unknown")
            imsi = system_info.get("IMSI", "unknown")
            mac_address = system_info.get("MacAddress", "unknown").strip()

            # Get system status (returns Pydantic model)
            system_status = self.api.system.get_status()
            status_dict = system_status.model_dump()

            # Get network info (requires login) - for detailed signal metrics
            network_info = None
            try:
                network_info = self.api.network.get_info()
            except Exception:
                pass

            # Get connection state (requires login)
            connection_state = None
            try:
                connection_state = self.api.network.get_connection_state()
            except Exception:
                pass

            # Get SMS storage state (public command, no login needed)
            sms_storage = None
            try:
                sms_storage = self.api.sms.get_storage_state()
            except Exception as e:
                # Log error but continue
                print(f"Warning: Could not get SMS storage state: {e}", file=sys.stderr)

            # Build metrics
            labels = f'imei="{imei}",imsi="{imsi}",mac_address="{mac_address}"'

            metrics = []

            # System Status Metrics
            metrics.append(f'battery_capacity_percent{{{labels}}} {status_dict.get("bat_cap", 0)}')
            metrics.append(f'battery_level{{{labels}}} {status_dict.get("bat_level", 0)}')
            metrics.append(f'current_connection_count{{{labels}}} {status_dict.get("curr_num", 0)}')
            metrics.append(f'total_connection_count{{{labels}}} {status_dict.get("TotalConnNum", 0)}')
            metrics.append(f'signal_strength{{{labels}}} {status_dict.get("SignalStrength", 0)}')
            metrics.append(f'roaming{{{labels}}} {status_dict.get("Roaming", 0)}')
            metrics.append(f'domestic_roaming{{{labels}}} {status_dict.get("Domestic_Roaming", 0)}')
            metrics.append(f'network_type{{{labels}}} {status_dict.get("NetworkType", 0)}')

            # Network Info Metrics (detailed signal info)
            if network_info:
                network_dict = network_info.model_dump()
                # Signal quality metrics (from Munin plugin)
                if network_dict.get("SINR") is not None:
                    metrics.append(f'sinr{{{labels}}} {int(network_dict.get("SINR", -999))}')
                if network_dict.get("RSRP") is not None:
                    metrics.append(f'rsrp{{{labels}}} {int(network_dict.get("RSRP", -999))}')
                if network_dict.get("RSSI") is not None:
                    metrics.append(f'rssi{{{labels}}} {int(network_dict.get("RSSI", -999))}')
                if network_dict.get("RSRQ") is not None:
                    metrics.append(f'rsrq{{{labels}}} {int(network_dict.get("RSRQ", -999))}')
                if network_dict.get("EcIo") is not None:
                    metrics.append(f'ecio{{{labels}}} {float(network_dict.get("EcIo", 0))}')
                if network_dict.get("RSCP") is not None:
                    metrics.append(f'rscp{{{labels}}} {int(network_dict.get("RSCP", -999))}')
                if network_dict.get("CellId") is not None:
                    metrics.append(f'cell_id{{{labels}}} {network_dict.get("CellId", 0)}')
                if network_dict.get("eNBID") is not None:
                    metrics.append(f'enb_id{{{labels}}} {network_dict.get("eNBID", 0)}')

            # Connection State Metrics
            if connection_state:
                conn_dict = connection_state.model_dump()
                metrics.append(f'connection_status{{{labels}}} {conn_dict.get("ConnectionStatus", 0)}')
                metrics.append(f'speed_download{{{labels}}} {conn_dict.get("Speed_Dl", 0)}')
                metrics.append(f'speed_upload{{{labels}}} {conn_dict.get("Speed_Ul", 0)}')
                metrics.append(f'download_rate{{{labels}}} {conn_dict.get("DlRate", 0)}')
                metrics.append(f'upload_rate{{{labels}}} {conn_dict.get("UlRate", 0)}')
                metrics.append(f'download_bytes{{{labels}}} {conn_dict.get("DlBytes", 0)}')
                metrics.append(f'upload_bytes{{{labels}}} {conn_dict.get("UlBytes", 0)}')
                metrics.append(f'connection_time{{{labels}}} {conn_dict.get("ConnectionTime", 0)}')

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
        return MetricsHandler(exporter, *args, **kwargs)
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
    api = AlcatelClient(args.url, args.password)

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

