from django.contrib import admin

from .models import Confession


@admin.register(Confession)
class ConfessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'short_text', 'status', 'views_count', 'likes_count', 'created_at')
    list_filter = ('status',)
    search_fields = ('text',)
    readonly_fields = ('id', 'created_at', 'moderated_at', 'views_count', 'likes_count')

    def short_text(self, obj):
        return (obj.text[:60] + '…') if len(obj.text) > 60 else obj.text
    short_text.short_description = 'Текст'
