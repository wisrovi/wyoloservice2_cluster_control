"""Lightweight static HTTP server for NeuralForge Cluster Admin VSCode Workbench SPA.

Serves ui/static/ on port 8501 with /health check and dynamic /config.js.
"""

import argparse
import json
import mimetypes
import os
import sys
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")


class WorkbenchHttpHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler serving the VSCode Workbench SPA."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def do_GET(self) -> None:  # noqa: N802
        """Handle GET requests with health checks, config injection and SPA routing."""
        # 1. Healthcheck endpoints (used by Docker and compose)
        if self.path in ("/health", "/_stcore/health", "/api/health"):
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            payload = json.dumps({"status": "healthy", "service": "cluster_admin_ui", "version": "3.2.0"})
            self.wfile.write(payload.encode("utf-8"))
            return

        # 2. Dynamic runtime config (/config.js)
        if self.path == "/config.js":
            cluster_api_env = os.environ.get("CLUSTER_API_URL", "")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/javascript")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()

            # If CLUSTER_API_URL is the internal docker network name (e.g. cluster_admin_api:8001),
            # the browser on the host machine won't resolve it. In that case, use window.location.hostname:8001.
            js_content = f"""
(function() {{
  var envUrl = "{cluster_api_env}".trim();
  var defaultHost = (window.location && window.location.hostname) ? window.location.hostname : "localhost";
  var resolvedUrl = "http://" + defaultHost + ":8001";

  if (envUrl && !envUrl.includes("cluster_admin_api")) {{
    resolvedUrl = envUrl.replace(/\\/$/, "");
  }}

  window.__CLUSTER_CONFIG__ = {{
    apiUrl: resolvedUrl,
    version: "3.0.1"
  }};
}})();
"""
            self.wfile.write(js_content.strip().encode("utf-8"))
            return

        # 3. Static files & SPA fallback
        clean_path = self.path.split("?")[0].lstrip("/")
        file_path = os.path.join(STATIC_DIR, clean_path)

        if not clean_path or not os.path.exists(file_path) or os.path.isdir(file_path):
            if clean_path and not os.path.exists(file_path) and ("." in os.path.basename(clean_path)):
                # Missing asset (e.g. missing .css or .png), return 404
                self.send_error(HTTPStatus.NOT_FOUND, f"File not found: {self.path}")
                return
            # Route to index.html for SPA routing
            self.path = "/index.html"

        super().do_GET()

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        """Log HTTP requests to stdout."""
        sys.stdout.write(f"[WorkbenchHTTP] {self.address_string()} - {format % args}\n")
        sys.stdout.flush()


def run_server(port: int = 8501, address: str = "0.0.0.0") -> None:
    """Start the ThreadingHTTPServer.

    Args:
        port: TCP port to bind.
        address: IP interface to bind.
    """
    mimetypes.init()
    mimetypes.add_type("text/css", ".css")
    mimetypes.add_type("application/javascript", ".js")
    mimetypes.add_type("image/svg+xml", ".svg")

    server_address = (address, port)
    httpd = ThreadingHTTPServer(server_address, WorkbenchHttpHandler)
    print(f"=== NeuralForge VSCode Workbench SPA v3.0.0 ===")
    print(f"Serving static assets from: {STATIC_DIR}")
    print(f"Listening on: http://{address}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Serve NeuralForge Cluster Admin VSCode Workbench SPA.")
    parser.add_argument("--port", type=int, default=int(os.environ.get("STREAMLIT_PORT", 8501)), help="Port to bind")
    parser.add_argument("--address", type=str, default=os.environ.get("STREAMLIT_ADDRESS", "0.0.0.0"), help="Address to bind")
    args = parser.parse_args()

    run_server(port=args.port, address=args.address)
