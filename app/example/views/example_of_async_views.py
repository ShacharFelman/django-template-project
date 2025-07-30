from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser
from drf_spectacular.utils import extend_schema
from example.services import ExampleOfAiService
from example.models import ExampleOfSummary, ExampleOfArticle
from example.serializers import ExampleOfModelSerializer
import logging

logger = logging.getLogger(__name__)

class ExampleOfAsyncProcessingView(APIView):
    """Example of a base view for async processing functionality."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ai_service = ExampleOfAiService()

@method_decorator(csrf_exempt, name='dispatch')
@extend_schema(
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'item_id': {'type': 'integer'},
                'processing_model': {'type': 'string'},
                'max_words': {'type': 'integer'},
            },
            'required': ['item_id']
        }
    },
    responses={200: {'type': 'object'}}
)
class ExampleOfAsyncProcessingView(ExampleOfAsyncProcessingView):
    """Example of a view to handle async processing requests."""
    def post(self, request):
        """
        Create a new processing request for an item. If processing is in progress, return status 202.
        """
        item_id = request.data.get('item_id')
        processing_model = request.data.get('processing_model', 'example-model-v1')
        max_words = request.data.get('max_words', 150)
        if not item_id:
            return Response({'error': 'item_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user if request.user.is_authenticated else None

        try:
            summary = self.ai_service.process_item_async(
                item_id=item_id,
                processing_model=processing_model,
                user=user,
                max_words=max_words
            )
        except ExampleOfArticle.DoesNotExist:
            return Response({'error': 'Example item not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            return Response({'error': 'Invalid input.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in async processing view: {str(e)}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = ExampleOfModelSerializer(summary)
        response_data = serializer.data

        if summary.status in ['pending', 'in_progress']:
            return Response({'success': True, 'summary': response_data, 'message': 'Processing is in progress.'}, status=status.HTTP_202_ACCEPTED)
        elif summary.status == 'completed':
            return Response({'success': True, 'summary': response_data}, status=status.HTTP_200_OK)
        elif summary.status == 'failed':
            return Response({'success': False, 'summary': response_data, 'message': 'Processing failed.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(responses={200: {'type': 'object'}})
class ExampleOfStatusCheckView(ExampleOfAsyncProcessingView):
    """Example of a view to retrieve processing status."""
    def get(self, request, item_id):
        """Get processing status for a specific item."""
        processing_model = request.GET.get('processing_model', 'example-model-v1')
        try:
            summary = self.ai_service.get_item_summary(
                item_id=item_id,
                processing_model=processing_model
            )
            if not summary:
                try:
                    ExampleOfArticle.objects.get(id=item_id)
                except ExampleOfArticle.DoesNotExist:
                    return Response({'error': 'Example item not found'}, status=status.HTTP_404_NOT_FOUND)
                return Response({'error': 'Processing summary not found'}, status=status.HTTP_404_NOT_FOUND)
            
            return Response({
                'success': True,
                'summary': {
                    'id': summary.id,
                    'item_id': summary.example_item.id,
                    'item_title': summary.example_item.title,
                    'summary_text': summary.summary_text,
                    'processing_model': summary.processing_model,
                    'status': summary.status,
                    'word_count': summary.word_count,
                    'processing_cost': summary.processing_cost,
                    'created_at': summary.created_at.isoformat(),
                    'completed_at': summary.completed_at.isoformat() if summary.completed_at else None
                }
            })
        except Exception as e:
            logger.error(f"Error in status check view: {str(e)}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(responses={200: {'type': 'object'}})
@api_view(["GET"])
@permission_classes([IsAdminUser])
@authentication_classes([TokenAuthentication])
def example_summary_status(request, summary_id):
    """Example of getting the status of a specific processing summary."""
    try:
        summary = ExampleOfSummary.objects.get(id=summary_id)
        return Response({
            'success': True,
            'status': {
                'id': summary.id,
                'status': summary.status,
                'created_at': summary.created_at.isoformat(),
                'completed_at': summary.completed_at.isoformat() if summary.completed_at else None,
                'error_message': summary.error_message
            }
        })
    except ExampleOfSummary.DoesNotExist:
        return Response({'error': 'Processing summary not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in summary status view: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 