"""
Проста автоматична модерація: перевірка тексту на заборонені слова.

Кожен новий запис створюється зі статусом PENDING ("на перевірці"),
після чого одразу проганяється через moderate_confession(), яка
переводить його у APPROVED (опубліковано) або REJECTED (відхилено).

Винесено в окремий модуль, щоб у майбутньому легко замінити
на асинхронну перевірку (Celery / AWS SQS + Lambda) без зміни
логіки в views.py.
"""
from django.conf import settings
from django.utils import timezone

from .models import Confession


def contains_banned_words(text: str) -> bool:
    normalized = text.lower()
    return any(word.lower() in normalized for word in settings.BANNED_WORDS)


def moderate_confession(confession: Confession) -> Confession:
    """Переводить запис зі стану PENDING у APPROVED або REJECTED."""
    if contains_banned_words(confession.text):
        confession.status = Confession.Status.REJECTED
    else:
        confession.status = Confession.Status.APPROVED

    confession.moderated_at = timezone.now()
    confession.save(update_fields=['status', 'moderated_at'])
    return confession
