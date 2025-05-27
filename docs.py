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
        "uv run python scripts/generate_docs.py",
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
    """Clean all generated documentation and build artifacts."""
    import shutil

    project_root = Path(__file__).parent
    
    paths_to_clean = [
        project_root / "site",                    # MkDocs build output
        project_root / ".mkdocs_cache",           # MkDocs cache
        project_root / "docs_src",                # Legacy docs directory
        project_root / "docs" / "schemas",        # Generated schema docs directory
    ]

    # Clean specific generated files
    schema_docs_dir = project_root / "docs" / "schemas"
    if schema_docs_dir.exists():
        for md_file in schema_docs_dir.glob("*.md"):
            if md_file.exists():
                md_file.unlink()
                print(f"🗑️  Removed file: {md_file.relative_to(project_root)}")

    # Clean directories
    for path in paths_to_clean:
        if path.exists() and path.is_dir():
            shutil.rmtree(path)
            print(f"🗑️  Removed directory: {path.relative_to(project_root)}")
    
    print("✅ Documentation cleanup completed")


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Documentation management for Standard Interfaces",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python docs.py install     # Install dependencies
  python docs.py generate    # Generate docs from schemas
  python docs.py serve       # Serve docs locally
  python docs.py build       # Build static site
  python docs.py deploy      # Deploy with versioning
  python docs.py clean       # Clean generated files
  
  # Full workflow
  python docs.py install generate serve
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
