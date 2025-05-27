#!/usr/bin/env python3
"""
Documentation management script for Standard Interfaces.
Provides easy commands for common documentation tasks.
"""

import argparse
import subprocess
import sys
import webbrowser
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✅ {description} completed")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(e.stderr)
        sys.exit(1)


def install_deps():
    """Install documentation dependencies."""
    run_command("uv sync --group docs", "Installing documentation dependencies")


def generate_docs():
    """Generate documentation from schemas."""
    run_command(
        "uv run python -m standard_interfaces.docs.generate_docs",
        "Generating documentation from schemas",
    )


def serve_docs(port=8000):
    """Serve documentation locally."""
    print(f"🚀 Starting development server on http://localhost:{port}")
    print("Press Ctrl+C to stop")

    try:
        # Open browser after a short delay
        import threading
        import time

        def open_browser():
            time.sleep(2)  # Give server time to start
            webbrowser.open(f"http://localhost:{port}")

        threading.Thread(target=open_browser, daemon=True).start()

        # Start MkDocs server
        subprocess.run(
            f"uv run mkdocs serve --dev-addr localhost:{port}", shell=True, check=True
        )

    except KeyboardInterrupt:
        print("\n👋 Documentation server stopped")


def build_docs():
    """Build static documentation."""
    run_command("uv run mkdocs build", "Building static documentation")
    print("📁 Documentation built in 'site/' directory")


def deploy_docs(version=None, alias=None):
    """Deploy documentation with versioning."""
    if not version:
        version = input("Enter version (e.g., 1.0): ")

    if not alias:
        alias = input("Enter alias (e.g., latest): ")

    cmd = f"uv run mike deploy --push --update-aliases {version} {alias}"
    run_command(cmd, f"Deploying documentation version {version}")

    # Set as default if it's 'latest'
    if alias == "latest":
        run_command(
            "uv run mike set-default --push latest", "Setting as default version"
        )


def clean_docs():
    """Clean generated documentation."""
    import shutil

    paths_to_clean = [
        Path("site"),
        *Path("docs/schemas").glob("*.md"),  # Auto-generated schema docs
    ]

    for path in paths_to_clean:
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
                print(f"🗑️  Removed directory: {path}")
            else:
                path.unlink()
                print(f"🗑️  Removed file: {path}")


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Documentation management for Standard Interfaces",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m standard_interfaces.docs.manage install     # Install dependencies
  python -m standard_interfaces.docs.manage generate    # Generate docs from schemas
  python -m standard_interfaces.docs.manage serve       # Serve docs locally
  python -m standard_interfaces.docs.manage build       # Build static site
  python -m standard_interfaces.docs.manage deploy      # Deploy with versioning
  python -m standard_interfaces.docs.manage clean       # Clean generated files
  
  # Full workflow
  python -m standard_interfaces.docs.manage install generate serve
        """,
    )

    parser.add_argument(
        "commands",
        nargs="+",
        choices=["install", "generate", "serve", "build", "deploy", "clean"],
        help="Commands to execute",
    )

    parser.add_argument(
        "--port", type=int, default=8000, help="Port for serve command (default: 8000)"
    )

    parser.add_argument("--version", help="Version for deploy command")

    parser.add_argument("--alias", help="Alias for deploy command")

    args = parser.parse_args()

    # Execute commands in order
    for command in args.commands:
        if command == "install":
            install_deps()
        elif command == "generate":
            generate_docs()
        elif command == "serve":
            serve_docs(args.port)
        elif command == "build":
            build_docs()
        elif command == "deploy":
            deploy_docs(args.version, args.alias)
        elif command == "clean":
            clean_docs()


if __name__ == "__main__":
    main()
