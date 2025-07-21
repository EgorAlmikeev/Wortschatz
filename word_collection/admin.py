from django.contrib import admin
from .models import Word, Category

@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ['definition', 'owner']
    list_filter = ['genus_id', 'categories']
    search_fields = ['owner__username']
    date_hierarchy = 'created_date_time'
    autocomplete_fields = ['owner', 'categories']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner']
    search_fields = ['owner__username']