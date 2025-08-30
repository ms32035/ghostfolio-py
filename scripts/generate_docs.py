#!/usr/bin/env python3
"""
Script to generate documentation locally using pdoc3.

Usage:
    python scripts/generate_docs.py
"""

import os
import subprocess
import sys
from pathlib import Path


def main():
    """Generate documentation using pdoc3."""
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    docs_dir = project_root / "docs"

    # Create docs directory if it doesn't exist
    docs_dir.mkdir(exist_ok=True)

    print("Generating documentation with pdoc3...")

    try:
        # Generate HTML documentation
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pdoc",
                "--html",
                "--output-dir",
                str(docs_dir),
                "ghostfolio",
            ],
            cwd=project_root,
            check=True,
            capture_output=True,
            text=True,
        )

        print("✅ Documentation generated successfully!")
        print(f"📁 Documentation saved to: {docs_dir}")

        # Create index.html redirect
        index_content = """<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="refresh" content="0; url=ghostfolio/index.html">
    <title>Ghostfolio Python Client Documentation</title>
</head>
<body>
    <p>Redirecting to <a href="ghostfolio/index.html">documentation</a>...</p>
</body>
</html>"""

        with open(docs_dir / "index.html", "w") as f:
            f.write(index_content)

        print("✅ Index redirect created!")

        # Open documentation in browser (optional)
        try:
            import webbrowser

            webbrowser.open(f"file://{docs_dir}/ghostfolio/index.html")
            print("🌐 Opening documentation in browser...")
        except Exception:
            print("💡 To view documentation, open: docs/ghostfolio/index.html")

    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating documentation: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
