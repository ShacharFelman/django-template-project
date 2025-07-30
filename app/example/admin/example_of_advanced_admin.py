from django.contrib import admin
from example.models import ExampleOfFetchLog

@admin.register(ExampleOfFetchLog)
class ExampleOfAdvancedAdmin(admin.ModelAdmin):
    """Example of advanced admin with filters and customizations."""
    list_display = ('source', 'status', 'started_at', 'completed_at',
                    'items_fetched', 'items_saved', 'duration_display')
    list_filter = ('status', 'started_at', 'source')
    search_fields = ('error_message', 'source')
    readonly_fields = ('started_at', 'completed_at', 'items_fetched',
                       'items_saved', 'duration_display', 'success_rate_display')
    date_hierarchy = 'started_at'
    ordering = ('-started_at',)
    
    def duration_display(self, obj):
        """Display duration in a readable format."""
        if obj.completed_at and obj.started_at:
            duration = obj.completed_at - obj.started_at
            return f"{duration.total_seconds():.2f}s"
        return "N/A"
    duration_display.short_description = "Duration"
    
    def success_rate_display(self, obj):
        """Display success rate as percentage."""
        if obj.items_fetched > 0:
            rate = (obj.items_saved / obj.items_fetched) * 100
            return f"{rate:.1f}%"
        return "N/A"
    success_rate_display.short_description = "Success Rate" 