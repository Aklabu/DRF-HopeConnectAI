from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Alert
from .services import FCMNotificationService
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Alert)
def send_alert_notification(sender, instance, created, **kwargs):
    """
    Signal handler to send push notifications when a new alert is created
    """
    if created:
        try:
            logger.info(f"New alert created, sending notifications: {instance.event}")
            FCMNotificationService.send_alert_notification(instance)
        except Exception as e:
            logger.error(f"Error in alert notification signal: {str(e)}")
