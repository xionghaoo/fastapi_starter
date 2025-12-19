from celery import Celery
from app.core.config import settings


def create_celery_app() -> Celery:
    app = Celery(
        "__APP_NAME__",
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend,
        include=["app.tasks"],
    )
    app.conf.update(
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone="UTC",
        enable_utc=True,
    )
    return app


celery_app = create_celery_app()


