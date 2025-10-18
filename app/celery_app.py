from celery import Celery
from celery.schedules import crontab

from app.users.models import User
from app.videos.models import Video, Subtitle
from app.oauth.models import SocialAccount
from app.logs.models import Log, Thread, UserContext


celery_app = Celery(
    "tasks",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
    include=["app.tasks"],
)


celery_app.autodiscover_tasks(["app.tasks"])
