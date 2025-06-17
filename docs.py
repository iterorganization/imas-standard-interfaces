#!/usr/bin/env python3
"""
Documentation management script for Standard Interfaces.
Provides easy commands for common documentation tasks.
"""

import shutil
import subprocess
import sys
from pathlib import Path

import click


def run_command(command, description, capture_output=True):
    """
    Run a command and handle errors.

    Args:
        command: Shell command to execute
        description: Description of what the command does
        capture_output: Whether to capture output (False for long-running processes)
    """
    print(f"🔄 {description}...")
    try:
        if capture_output:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                capture_output=True,
                text=True,
            )
            if result.stdout:
                print(result.stdout)
            return result
        else:
            # For long-running processes like servers, don't capture output
            subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if hasattr(e, "stderr") and e.stderr:
            print(f"Error output: {e.stderr}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        sys.exit(0)


@click.group()
def cli():
    """Documentation management for Standard Interfaces."""
    pass


@cli.command()
def install():
    """Install documentation dependencies."""
    run_command("uv sync --group docs", "Installing documentation dependencies")


@cli.command()
def generate():
    """Generate documentation from schemas."""
    run_command(
        "uv run python scripts/generate_docs.py",
        "Generating documentation from schemas",
    )


@cli.command()
@click.option("--port", "-p", default=8000, help="Port to serve on")
@click.option("--host", "-h", default="127.0.0.1", help="Host to bind to")
def dev_serve(port, host):
    """Serve documentation in development mode (no versioning)."""
    cmd = f"uv run mkdocs serve --dev-addr {host}:{port}"
    print(f"🌐 Server will be available at http://{host}:{port}")
    print("📝 Press Ctrl+C to stop the server")
    run_command(
        cmd, f"Starting development server on {host}:{port}", capture_output=False
    )


@cli.command()
@click.option("--port", "-p", default=8000, help="Port to serve on")
@click.option("--host", "-h", default="127.0.0.1", help="Host to bind to")
def serve(port, host):
    """Serve documentation with versioning (production mode)."""
    # Check if site directory exists
    site_dir = Path("site")
    if not site_dir.exists():
        print("⚠️  No site directory found. Building initial version...")
        deploy_initial_version()

    cmd = f"uv run mike serve --dev-addr {host}:{port}"
    print(f"🌐 Server will be available at http://{host}:{port}")
    print("📝 Press Ctrl+C to stop the server")
    run_command(cmd, f"Starting mike server on {host}:{port}", capture_output=False)


@cli.command()
def build():
    """Build static documentation."""
    run_command("uv run mkdocs build", "Building static documentation")
    print("📁 Documentation built in 'site/' directory")


@cli.command()
@click.option("--version", "-v", help="Version to deploy")
@click.option("--alias", "-a", help="Alias for the version (e.g., latest)")
@click.option("--push/--no-push", default=False, help="Push to git remote")
def deploy(version, alias, push):
    """Deploy documentation with versioning."""
    if not version:
        version = click.prompt("Enter version to deploy", default="dev")

    if not alias:
        alias = click.prompt("Enter alias", default="latest")

    push_flag = "--push" if push else ""
    cmd = f"uv run mike deploy {push_flag} --update-aliases {version} {alias}"
    run_command(cmd, f"Deploying documentation version {version}")

    # Set as default if it's 'latest'
    if alias == "latest":
        set_default_cmd = f"uv run mike set-default {push_flag} {alias}"
        run_command(set_default_cmd, "Setting as default version")


@cli.command()
def clean():
    """Clean generated documentation files."""
    paths_to_clean = ["site/", "docs/schemas/", "docs/static/"]

    for path in paths_to_clean:
        path_obj = Path(path)
        if path_obj.exists():
            if path_obj.is_dir():
                shutil.rmtree(path_obj)
                print(f"🗑️  Removed directory: {path}")
            else:
                path_obj.unlink()
                print(f"🗑️  Removed file: {path}")

    print("✅ Documentation cleanup complete")


def deploy_initial_version():
    """Deploy an initial development version for mike to serve."""
    print("🚀 Deploying initial development version...")
    run_command(
        "uv run mike deploy --update-aliases dev latest", "Creating initial version"
    )
    run_command("uv run mike set-default latest", "Setting latest as default")


if __name__ == "__main__":
    cli()
