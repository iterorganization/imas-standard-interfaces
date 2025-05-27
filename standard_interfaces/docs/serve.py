#!/usr/bin/env python3
"""
Simple HTTP server for serving JSON schema documentation.
Run this script to serve the documentation locally.
"""

import http.server
import socketserver
import webbrowser
import os
from pathlib import Path


def serve_docs(port=8000):
    """Serve the documentation on the specified port."""

    # Change to the project root directory (3 levels up from this file)
    project_root = Path(__file__).parent.parent.parent
    os.chdir(project_root)

    # Create a custom handler to set CORS headers
    class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "*")
            super().end_headers()

    with socketserver.TCPServer(("", port), CORSHTTPRequestHandler) as httpd:
        print(f"Serving documentation at http://localhost:{port}")
        print(f"Schema viewer: http://localhost:{port}/docs/schema-viewer.html")
        print(f"Redoc viewer: http://localhost:{port}/docs/index.html")
        print("Press Ctrl+C to stop the server")

        # Open browser automatically
        webbrowser.open(f"http://localhost:{port}/docs/schema-viewer.html")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down the server...")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Serve documentation locally")
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to serve on (default: 8000)"
    )
    args = parser.parse_args()

    serve_docs(args.port)


if __name__ == "__main__":
    main()
