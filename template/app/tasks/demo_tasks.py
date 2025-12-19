from app.tasks.celery import celery_app


@celery_app.task(name="demo.echo")
def echo(value: str) -> str:
    return value


