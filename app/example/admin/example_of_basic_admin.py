from django.contrib import admin
from example.models import ExampleOfArticle

class ExampleOfBasicAdmin(admin.ModelAdmin):
    """Example of basic admin customization."""
    readonly_fields = ('id', 'created_at')
    list_display = ('id', 'title', 'author', 'source', 'published_date', 'created_at')
    list_filter = ('source', 'published_date', 'created_at')
    search_fields = ('title', 'content', 'author')
    ordering = ('-published_date',)
    date_hierarchy = 'published_date'

admin.site.register(ExampleOfArticle, ExampleOfBasicAdmin) 