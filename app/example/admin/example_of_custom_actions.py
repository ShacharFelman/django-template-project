from django.contrib import admin
from example.models import ExampleOfSummary

@admin.register(ExampleOfSummary)
class ExampleOfCustomActionsAdmin(admin.ModelAdmin):
    """Example of admin with custom actions and advanced features."""

    list_display = [
        'item_title_short',
        'processing_model',
        'status',
        'word_count',
        'processing_cost',
        'created_at',
        'completed_at'
    ]

    list_filter = [
        'processing_model',
        'status',
        'created_at',
        'completed_at'
    ]

    search_fields = [
        'example_item__title',
        'example_item__source',
        'summary_text'
    ]

    readonly_fields = [
        'created_at',
        'completed_at',
        'processing_cost'
    ]

    fieldsets = (
        ('Item Information', {
            'fields': ('example_item', 'processing_model', 'requested_by')
        }),
        ('Summary', {
            'fields': ('summary_text', 'word_count', 'status')
        }),
        ('Metadata', {
            'fields': ('processing_cost', 'created_at', 'completed_at')
        }),
        ('Error Information', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        })
    )

    ordering = ['-created_at']

    def item_title_short(self, obj):
        """Display shortened item title."""
        return obj.example_item.title[:50] + "..." if len(obj.example_item.title) > 50 else obj.example_item.title
    item_title_short.short_description = "Item Title"

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('example_item', 'requested_by')

    actions = ['mark_as_pending', 'mark_as_failed', 'recalculate_cost']

    def mark_as_pending(self, request, queryset):
        """Mark selected summaries as pending."""
        updated = queryset.update(status='pending', error_message=None)
        self.message_user(request, f'{updated} summaries marked as pending.')
    mark_as_pending.short_description = "Mark selected summaries as pending"

    def mark_as_failed(self, request, queryset):
        """Mark selected summaries as failed."""
        updated = queryset.update(status='failed')
        self.message_user(request, f'{updated} summaries marked as failed.')
    mark_as_failed.short_description = "Mark selected summaries as failed"

    def recalculate_cost(self, request, queryset):
        """Recalculate processing cost for selected summaries."""
        updated = 0
        for summary in queryset:
            if summary.summary_text:
                # Example cost calculation: 0.001 per word
                summary.processing_cost = len(summary.summary_text.split()) * 0.001
                summary.save()
                updated += 1
        self.message_user(request, f'Processing cost recalculated for {updated} summaries.')
    recalculate_cost.short_description = "Recalculate processing cost" 