from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from .models import Alert
from .serializers import AlertSerializer
import logging
from drf_spectacular.utils import extend_schema

logger = logging.getLogger(__name__)


class AlertListView(APIView):
    """
    API View to list weather alerts with pagination and filtering
    Only authenticated users can access this endpoint
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AlertSerializer

    @extend_schema(
        operation_id="alerts_list",
        responses=AlertSerializer(many=True)
    )
    
    def get(self, request):
        """
        Get paginated list of weather alerts
        Query parameters:
        - page: Page number (default: 1)
        - page_size: Items per page (default: 20, max: 100)
        - severity: Filter by severity level
        """
        try:
            # Get query parameters
            page = int(request.query_params.get('page', 1))
            page_size = min(int(request.query_params.get('page_size', 20)), 100)
            severity_filter = request.query_params.get('severity')
            
            # Validate page parameters
            if page < 1:
                return Response(
                    {'error': 'Page number must be greater than 0'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if page_size < 1:
                return Response(
                    {'error': 'Page size must be greater than 0'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Build queryset
            queryset = Alert.objects.all()
            
            # Apply severity filter if provided
            if severity_filter:
                valid_severities = [choice[0] for choice in Alert.SEVERITY_CHOICES]
                if severity_filter not in valid_severities:
                    return Response(
                        {
                            'error': f'Invalid severity. Valid options: {", ".join(valid_severities)}'
                        }, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                queryset = queryset.filter(severity=severity_filter)
            
            # Paginate results
            paginator = Paginator(queryset, page_size)
            
            if page > paginator.num_pages:
                return Response(
                    {'error': f'Page {page} does not exist. Total pages: {paginator.num_pages}'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            page_obj = paginator.get_page(page)
            serializer = AlertSerializer(page_obj, many=True)
            
            return Response({
                'count': paginator.count,
                'total_pages': paginator.num_pages,
                'current_page': page,
                'page_size': page_size,
                'results': serializer.data
            })
            
        except ValueError:
            return Response(
                {'error': 'Invalid page or page_size parameter'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error in AlertListView: {str(e)}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AlertDetailView(APIView):
    """
    API View to retrieve a specific weather alert by ID
    Only authenticated users can access this endpoint
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AlertSerializer

    @extend_schema(
        operation_id="alerts_retrieve",
        responses=AlertSerializer
    )
    
    def get(self, request, alert_id):
        """
        Get specific alert by ID
        """
        try:
            alert = Alert.objects.get(id=alert_id)
            serializer = AlertSerializer(alert)
            return Response(serializer.data)
            
        except Alert.DoesNotExist:
            return Response(
                {'error': 'Alert not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError:
            return Response(
                {'error': 'Invalid alert ID format'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error in AlertDetailView: {str(e)}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
