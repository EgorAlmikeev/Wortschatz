from django.contrib import admin
from .models import Word, Tag


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ["definition", "owner"]
    list_filter = ["genus_id", "part_of_speech_id"]
    search_fields = ["owner__username"]
    date_hierarchy = "created_date_time"
    autocomplete_fields = ["owner"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "owner"]
    search_fields = ["owner__username"]
