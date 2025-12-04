
import os
import argparse
from pathlib import Path
import logging
import json
print()
# ログ設定
logging.basicConfig(level=logging.INFO, format="✅ %(message)s")

# テンプレート定義
PYPROJECT_TEMPLATE = """[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{package_name}"
version = "0.1.0"
description = "Auto-generated Python package structure"
authors = [
    {{ name = "{author_name}", email = "{author_email}" }}
]
readme = "README.md"
requires-python = ">=3.9"
dependencies = [{dependencies}]
"""

README_TEMPLATE = "# {package_name}\n\nThis is an auto-generated Python package structure.\n"

MAIN_TEMPLATE = """def main():
    print("Hello from {package_name}!")

if __name__ == "__main__":
    main()
"""

GITIGNORE_TEMPLATE = """venv/
__pycache__/
*.pyc
.env
log/
"""

ENV_TEMPLATE = "# Environment variables go here\n"

DEFAULT_CONFIG = {
    "setting": "default",
    "debug": True
}

PRODUCTION_CONFIG = {
    "setting": "production",
    "debug": False
}


def normalize_dependencies(deps: str) -> str:
    """Convert comma-separated deps into quoted list."""
    return ', '.join(f'"{d.strip()}"' for d in deps.split(",") if d.strip())


def create_structure(package_name: str, deps: str, author_name: str, author_email: str):
    root = Path(package_name)
    src_dir = root / "src" / package_name
    tests_dir = root / "tests"
    config_dir = src_dir / "config"
    venv_dir = root / "venv"

    # 追加ディレクトリ（tests と同階層＝root 直下）
    assets_dir = root / "assets"
    build_dir = root / "build"
    log_dir = root / "log"

    # ディレクトリ作成
    for path in [
        src_dir / "modules",
        src_dir / "utils",
        tests_dir,
        config_dir,
        venv_dir,
        assets_dir,  # root/assets
        build_dir,   # root/build
        log_dir      # root/log
    ]:
        os.makedirs(path, exist_ok=True)

    # 依存パッケージ整形
    deps_formatted = normalize_dependencies(deps)

    # ファイル作成
    files = {
        src_dir / "__init__.py": "",
        src_dir / "main.py": MAIN_TEMPLATE.format(package_name=package_name),
        root / "pyproject.toml": PYPROJECT_TEMPLATE.format(
            package_name=package_name,
            author_name=author_name or "Kota Kawano",
            author_email=author_email or "",
            dependencies=deps_formatted,
        ),
        root / "README.md": README_TEMPLATE.format(package_name=package_name),
        tests_dir / "test_sample.py": "def test_sample():\n    assert True\n",
        root / ".gitignore": GITIGNORE_TEMPLATE,
        root / ".env": ENV_TEMPLATE,
        config_dir / "default.json": json.dumps(DEFAULT_CONFIG, indent=4),
        config_dir / "production.json": json.dumps(PRODUCTION_CONFIG, indent=4),
    }

    for path, content in files.items():
        path.write_text(content, encoding="utf-8")

    # ログ出力
    logging.info(
        f"Package structure for '{package_name}' created successfully!")
    if deps_formatted:
        logging.info(f"Dependencies: [{deps_formatted}]")
    logging.info(
        f"Author: {author_name or 'Your Name'} <{author_email or 'your_email@example.com'}>")


def main():
    parser = argparse.ArgumentParser(
        description="Create Python package structure")
    parser.add_argument("--name", required=True, help="Package name")
    parser.add_argument("--deps", nargs="?", const="", default="",
                        help="Comma-separated dependencies (optional)")
    parser.add_argument("--author-name", default="", help="Author name")
    parser.add_argument("--author-email", default="", help="Author email")
    args = parser.parse_args()

    create_structure(args.name, args.deps, args.author_name, args.author_email)


if __name__ == "__main__":
    main()
