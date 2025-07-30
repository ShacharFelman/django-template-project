from django.urls import path, include
from rest_framework.routers import DefaultRouter
from example.views import (
    ExampleOfCachedListView,
    ExampleOfManualTriggerView,
    ExampleOfAsyncProcessingView,
    ExampleOfStatusCheckView,
    example_summary_status
)

# Create a router for the CRUD views
router = DefaultRouter()
router.register(r'items', ExampleOfCachedListView, basename='example-item')

urlpatterns = [
    # CRUD examples
    path('', include(router.urls)),
    
    # Service examples
    path('fetch/', ExampleOfManualTriggerView.as_view(), name='example-fetch'),
    
    # Async examples
    path('process/', ExampleOfAsyncProcessingView.as_view(), name='example-process'),
    path('status/<int:item_id>/', ExampleOfStatusCheckView.as_view(), name='example-status'),
    path('summary-status/<int:summary_id>/', example_summary_status, name='example-summary-status'),
] 