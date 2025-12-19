## fastapi_starter

FastAPI 脚手架项目创建器：基于模板快速生成一个带 MySQL、Redis、日志与 Alembic 的 FastAPI 项目。

### 1) 目录文本替换脚本

```bash
python fastapi_starter/replace_text.py --root ./my_project \
  --from __APP_NAME__ --to my_project \
  --include "**/*.py" --include "**/*.toml" --include "**/*.md"
```

### 2) 生成新项目

```bash
python fastapi_starter/generate.py \
  --name my_project \
  --mysql-host 127.0.0.1 --mysql-port 3306 --mysql-db mydb \
  --mysql-user user --mysql-password password \
  --redis-host 127.0.0.1 --redis-port 6379 --redis-db 0 \
  --celery-broker-url redis://127.0.0.1:6379/1 \
  --celery-result-backend redis://127.0.0.1:6379/2 \
  --log-level INFO --log-dir logs
```

交互模式（不带参数时会提示逐项输入）：

```bash
python fastapi_starter/generate.py
# 按提示输入项目名、MySQL/Redis 配置、日志等
```

生成完成后：

```bash
cd my_project
poetry install
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

可选：使用 Docker（开发）

```bash
cd docker
./start_services.sh   # 启动 web、worker、mysql、redis
# 访问 http://localhost:8000/docs
./stop_services.sh    # 停止所有服务
```

### 3) 模板说明

- `app/core`: 配置与日志
- `app/repo`: SQLAlchemy 基础与 Session
- `app/api`: 统一错误与响应
- `app/tasks`: Celery 配置与示例任务
- `alembic/`: 数据库迁移配置（`alembic.ini` 会替换为你的 MySQL URL）
- `pyproject.toml`: 依赖定义
- `env.example`: 环境变量示例（生成器会写入 `.env`）
- `docker/`: `Dockerfile`、`docker-compose.yml`、启动/停止脚本


