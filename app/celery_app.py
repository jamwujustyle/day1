from celery import Celery

from app.users.models import User
from app.videos.models.video import Video
from app.oauth.models import SocialAccount
from app.videos.models.subtitle import Subtitle


celery_app = Celery(
    "tasks",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
    include=["app.tasks"],
)

celery_app.autodiscover_tasks(["app.tasks"])
