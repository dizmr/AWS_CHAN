import uuid

from django.db import models


class Confession(models.Model):
    """
    Анонімний запис на дошці зізнань.

    Логіка станів:
      PENDING   -> запис щойно створено, ще не пройшов перевірку
      APPROVED  -> пройшов автоматичну перевірку на заборонені слова,
                   видимий у публічній стрічці
      REJECTED  -> містить заборонені слова, приховано від публіки
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'На перевірці'
        APPROVED = 'approved', 'Опубліковано'
        REJECTED = 'rejected', 'Відхилено'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField(max_length=1000)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    moderated_at = models.DateTimeField(null=True, blank=True)

    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Зізнання'
        verbose_name_plural = 'Зізнання'

    def __str__(self):
        preview = (self.text[:40] + '…') if len(self.text) > 40 else self.text
        return f'[{self.get_status_display()}] {preview}'
