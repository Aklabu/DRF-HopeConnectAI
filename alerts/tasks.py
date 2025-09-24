import requests
import logging
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Alert
from .services import FCMNotificationService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_weather_alerts_task(self):
    """
    Celery task to fetch weather alerts from National Weather Service API
    Runs every 30 minutes via Celery Beat
    """
    try:
        # API endpoint for Nevada weather alerts
        api_url = "https://api.weather.gov/alerts/active?area=NV"
        
        # Set appropriate headers for NWS API
        headers = {
            'User-Agent': 'Weather Alert App (contact@yourapp.com)',
            'Accept': 'application/json'
        }
        
        logger.info("Fetching weather alerts from NWS API")
        
        # Make API request
        response = requests.get(api_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        features = data.get('features', [])
        
        new_alerts_count = 0
        
        for feature in features:
            try:
                properties = feature.get('properties', {})
                source_id = feature.get('id')
                
                if not source_id:
                    logger.warning("Skipping alert with missing ID")
                    continue
                
                # Check if alert already exists
                if Alert.objects.filter(source_id=source_id).exists():
                    continue
                
                # Create new alert
                alert = Alert.objects.create(
                    source_id=source_id,
                    event=properties.get('event', '')[:200],  # Limit to field max length
                    headline=properties.get('headline', '')[:500],
                    description=properties.get('description', ''),
                    severity=properties.get('severity', 'Minor'),
                    area=properties.get('areaDesc', '')[:500]
                )
                
                new_alerts_count += 1
                logger.info(f"Created new alert: {alert.event} - {alert.area}")
                
            except Exception as e:
                logger.error(f"Error processing individual alert: {str(e)}")
                continue
        
        logger.info(f"Task completed. New alerts created: {new_alerts_count}")
        return f"Successfully processed {len(features)} alerts, created {new_alerts_count} new alerts"
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        # Retry on network errors
        raise self.retry(exc=e)
        
    except Exception as e:
        logger.error(f"Unexpected error in fetch_weather_alerts_task: {str(e)}")
        raise


@shared_task
def expire_alerts_task():
    """
    Optional task to clean up old alerts
    Remove alerts older than 7 days
    """
    try:
        cutoff_date = timezone.now() - timedelta(days=7)
        deleted_count, _ = Alert.objects.filter(created_at__lt=cutoff_date).delete()
        
        logger.info(f"Expired {deleted_count} old alerts")
        return f"Expired {deleted_count} old alerts"
        
    except Exception as e:
        logger.error(f"Error in expire_alerts_task: {str(e)}")
        raise
