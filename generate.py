#!/usr/bin/env python3
import argparse
import os
import sys
import shutil
from pathlib import Path
from typing import Dict, Iterable, List, Tuple
import getpass


PLACEHOLDERS: Tuple[str, ...] = (
    "__APP_NAME__",
    "__MYSQL_URL__",
    "__REDIS_URL__",
    "__CELERY_BROKER_URL__",
    "__CELERY_RESULT_BACKEND__",
    "__LOG_LEVEL__",
    "__LOG_DIR__",
)

TEXT_FILE_EXTS: Tuple[str, ...] = (
    ".py",
    ".toml",
    ".md",
    ".ini",
    ".txt",
    ".env",
    ".cfg",
    ".yaml",
    ".yml",
)


def build_mysql_url(user: str, password: str, host: str, port: int, database: str) -> str:
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"


def build_redis_url(host: str, port: int, db: int) -> str:
    return f"redis://{host}:{port}/{db}"

def build_celery_urls_from_redis(host: str, port: int) -> Tuple[str, str]:
    return (f"redis://{host}:{port}/1", f"redis://{host}:{port}/2")


def copy_template(template_dir: Path, target_dir: Path) -> None:
    if target_dir.exists():
        raise SystemExit(f"Target directory already exists: {target_dir}")
    shutil.copytree(template_dir, target_dir)


def iter_project_files(root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != "__pycache__" and not d.startswith(".")]
        for filename in filenames:
            if filename.startswith("."):
                continue
            yield Path(dirpath) / filename


def replace_placeholders(root: Path, mapping: Dict[str, str]) -> None:
    for file_path in iter_project_files(root):
        if file_path.suffix not in TEXT_FILE_EXTS:
            # keep binaries (images, etc.)
            continue
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            continue
        original = content
        for key, value in mapping.items():
            content = content.replace(key, value)
        if content != original:
            file_path.write_text(content, encoding="utf-8")


def write_env_file(root: Path, env_values: Dict[str, str]) -> None:
    lines: List[str] = [f"{k}={v}" for k, v in env_values.items()]
    (root / ".env").write_text("\n".join(lines) + "\n", encoding="utf-8")


def prompt_str(label: str, default: str | None = None, required: bool = False) -> str:
    while True:
        suffix = f" [{default}]" if default is not None else ""
        value = input(f"{label}{suffix}: ").strip()
        if not value and default is not None:
            return default
        if value:
            return value
        if not required:
            return ""
        print("Value is required.")


def prompt_int(label: str, default: int | None = None, required: bool = False) -> int:
    while True:
        suffix = f" [{default}]" if default is not None else ""
        raw = input(f"{label}{suffix}: ").strip()
        if not raw and default is not None:
            return default
        if not raw and not required:
            return 0 if default is None else default
        try:
            return int(raw)
        except ValueError:
            print("Please enter a valid integer.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a new FastAPI project from template.")
    parser.add_argument("--name", help="Project name (and target folder name)")
    parser.add_argument("--mysql-host")
    parser.add_argument("--mysql-port", type=int)
    parser.add_argument("--mysql-db")
    parser.add_argument("--mysql-user")
    parser.add_argument("--mysql-password")
    parser.add_argument("--redis-host")
    parser.add_argument("--redis-port", type=int)
    parser.add_argument("--redis-db", type=int)
    parser.add_argument("--celery-broker-url", default=None, help="Override Celery broker URL (default: redis db 1)")
    parser.add_argument("--celery-result-backend", default=None, help="Override Celery result backend (default: redis db 2)")
    parser.add_argument("--log-level")
    parser.add_argument("--log-dir")

    args = parser.parse_args()

    workspace = Path.cwd()
    template_dir = Path(__file__).resolve().parent / "template"

    name = args.name or prompt_str("Project name", required=True)
    target_dir = workspace / name

    mysql_host = args.mysql_host or prompt_str("MySQL host", default="127.0.0.1", required=True)
    mysql_port = args.mysql_port if args.mysql_port is not None else prompt_int("MySQL port", default=3306, required=True)
    mysql_db = args.mysql_db or prompt_str("MySQL database", default=name, required=True)
    mysql_user = args.mysql_user or prompt_str("MySQL user", default="user", required=True)
    mysql_password = args.mysql_password or getpass.getpass("MySQL password: ")
    if not mysql_password:
        print("MySQL password is required.")
        sys.exit(1)

    redis_host = args.redis_host or prompt_str("Redis host", default="127.0.0.1", required=True)
    redis_port = args.redis_port if args.redis_port is not None else prompt_int("Redis port", default=6379, required=True)
    redis_db = args.redis_db if args.redis_db is not None else prompt_int("Redis db", default=0, required=True)

    log_level = args.log_level or prompt_str("Log level", default="INFO", required=True)
    log_dir = args.log_dir or prompt_str("Log directory", default="logs", required=True)

    mysql_url = build_mysql_url(mysql_user, mysql_password, mysql_host, mysql_port, mysql_db)
    redis_url = build_redis_url(redis_host, redis_port, redis_db)
    if args.celery_broker_url and args.celery_result_backend:
        celery_broker_url = args.celery_broker_url
        celery_result_backend = args.celery_result_backend
    else:
        celery_broker_url, celery_result_backend = build_celery_urls_from_redis(redis_host, redis_port)
        # Allow interactive override
        override = prompt_str("Override Celery URLs? (y/N)", default="N").lower()
        if override == "y":
            celery_broker_url = prompt_str("Celery broker URL", default=celery_broker_url, required=True)
            celery_result_backend = prompt_str("Celery result backend", default=celery_result_backend, required=True)

    copy_template(template_dir, target_dir)

    mapping = {
        "__APP_NAME__": name,
        "__MYSQL_URL__": mysql_url,
        "__REDIS_URL__": redis_url,
        "__CELERY_BROKER_URL__": celery_broker_url,
        "__CELERY_RESULT_BACKEND__": celery_result_backend,
        "__LOG_LEVEL__": log_level,
        "__LOG_DIR__": log_dir,
    }
    replace_placeholders(target_dir, mapping)

    write_env_file(
        target_dir,
        {
            "ENVIRONMENT": "development",
            "APP_NAME": name,
            "MYSQL_URL": mysql_url,
            "REDIS_URL": redis_url,
            "CELERY_BROKER_URL": celery_broker_url,
            "CELERY_RESULT_BACKEND": celery_result_backend,
            "LOG_LEVEL": log_level,
            "LOG_DIR": log_dir,
        },
    )

    print(f"Project created at: {target_dir}")
    print("Next steps:")
    print(f"  cd {name}")
    print("  poetry install")
    print("  poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
    print("Docker (optional):")
    print("  cd docker")
    print("  ./start_services.sh")
    print("  ./stop_services.sh")


if __name__ == "__main__":
    main()


