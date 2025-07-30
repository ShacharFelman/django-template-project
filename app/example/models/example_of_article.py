from django.utils import timezone
from django.db import models

class ExampleOfArticle(models.Model):
    """ Example of a basic model with relationships and common fields. """
    title = models.CharField(max_length=255, help_text="The title of the example item.")
    content = models.TextField(help_text="The full content of the example item.")
    url = models.URLField(unique=True, help_text="The original URL of the example item.")
    published_date = models.DateTimeField(help_text="The date and time when the item was published.")
    author = models.CharField(max_length=100, blank=True, null=True, help_text="The author of the example item.")
    source = models.CharField(max_length=100, help_text="The source of the example item.")
    image_url = models.URLField(blank=True, null=True, help_text="An optional image URL for the example item.")
    description = models.TextField(blank=True, null=True, help_text="A brief description or summary of the example item.")
    example_source = models.CharField(max_length=100, help_text="The example source of the item.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="The date and time when the item was created.")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-published_date']
        verbose_name = "Example Article"
        verbose_name_plural = "Example Articles" 