
from django.conf import settings
from django.utils import timezone

from .models import Confession


def contains_banned_words(text: str) -> bool:
    normalized = text.lower()
    return any(word.lower() in normalized for word in settings.BANNED_WORDS)


def moderate_confession(confession: Confession) -> Confession:
    if contains_banned_words(confession.text):
        confession.status = Confession.Status.REJECTED
    else:
        confession.status = Confession.Status.APPROVED

    confession.moderated_at = timezone.now()
    confession.save(update_fields=['status', 'moderated_at'])
    return confession
