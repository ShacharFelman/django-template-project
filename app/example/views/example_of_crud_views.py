from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from core.permissions import ExampleOfCustomPermission
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.authentication import TokenAuthentication

from example.models import ExampleOfArticle
from example.serializers import ExampleOfCustomValidationSerializer

import logging

logger = logging.getLogger(__name__)

class ExampleOfCachedListView(viewsets.ModelViewSet):
    """
    Example of a viewset with caching and custom permissions.
    This viewset provides `list`, `create`, `retrieve`, `update`, and `destroy` actions.
    Methods:
        - GET: List all example items
        - POST: Create a new example item
        - GET {id}/: Retrieve a specific example item by ID
        - PUT {id}/: Update a specific example item by ID
        - DELETE {id}/: Delete a specific example item by ID

    * The items are ordered by their published date in descending order.
    * Includes caching for GET requests (5 minutes).
    """

    queryset = ExampleOfArticle.objects.all().order_by('-published_date')
    serializer_class = ExampleOfCustomValidationSerializer
    permission_classes = [ExampleOfCustomPermission]
    authentication_classes = [TokenAuthentication]

    # Cache GET list endpoint (5 minutes)
    @method_decorator(cache_page(60 * 5), name='list')
    @method_decorator(cache_page(60 * 5), name='retrieve')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    @method_decorator(cache_page(60 * 5))
    @action(detail=True, methods=['get'], url_path='process')
    def process(self, request, pk=None):
        """Example of a custom action that processes an item asynchronously."""
        try:
            example_item = ExampleOfArticle.objects.get(id=pk)
        except ExampleOfArticle.DoesNotExist:
            return Response({'detail': 'Example item not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            # Example processing logic
            logger.info(f"Processing example item: {example_item.title}")
            return Response({
                'success': True, 
                'message': 'Example item is being processed.',
                'item_id': pk
            }, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            logger.error(f"Error in ExampleOfCachedListView.process: {str(e)}")
            return Response({'error': 'Internal server error.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 