import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Confession',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('text', models.TextField(max_length=1000)),
                ('status', models.CharField(
                    choices=[('pending', 'На перевірці'), ('approved', 'Опубліковано'), ('rejected', 'Відхилено')],
                    default='pending', db_index=True, max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('moderated_at', models.DateTimeField(blank=True, null=True)),
                ('views_count', models.PositiveIntegerField(default=0)),
                ('likes_count', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Зізнання',
                'verbose_name_plural': 'Зізнання',
                'ordering': ['-created_at'],
            },
        ),
    ]
