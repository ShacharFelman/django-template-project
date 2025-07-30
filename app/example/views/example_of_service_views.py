"""Example of service views for external API integration."""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from example.services import ExampleOfExternalApiService, ExampleServiceError
from rest_framework.permissions import IsAdminUser
from rest_framework.authentication import TokenAuthentication

import logging
logger = logging.getLogger(__name__)


class ExampleOfManualTriggerView(APIView):
    """Example of a view to manually trigger external API service."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def post(self, request):
        query_params = request.data.get('query_params', None)
        try:
            service = ExampleOfExternalApiService()
            service.fetch_and_save(query_params, source='ExampleService')
            return Response({'message': 'Example fetch and save completed successfully.'}, status=status.HTTP_200_OK)
        except ExampleServiceError as e:
            logger.error(f"ExampleServiceError in ExampleOfManualTriggerView: {str(e)}")
            return Response({'error': 'Internal server error.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Unexpected error in ExampleOfManualTriggerView: {str(e)}")
            return Response({'error': 'Internal server error.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 