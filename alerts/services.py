import json
import logging
from firebase_admin import messaging
from django.conf import settings
from accounts.models import CustomUser

logger = logging.getLogger(__name__)


class FCMNotificationService:
    """
    Service class to handle Firebase Cloud Messaging notifications
    """
    
    @staticmethod
    def send_alert_notification(alert):
        """
        Send push notification for a new weather alert
        """
        try:
            # Get all users with firebase tokens
            users_with_tokens = CustomUser.objects.filter(
                firebase_token__isnull=False
            ).exclude(firebase_token='')
            
            if not users_with_tokens.exists():
                logger.info("No users with firebase tokens found")
                return
            
            # Extract tokens
            tokens = [user.firebase_token for user in users_with_tokens]
            
            # Create notification payload
            notification = messaging.Notification(
                title=alert.event,
                body=alert.headline
            )
            
            # Create data payload
            data = {
                'alert_id': str(alert.id),
                'severity': alert.severity,
                'area': alert.area,
                'type': 'weather_alert'
            }
            
            # Create multicast message
            message = messaging.MulticastMessage(
                notification=notification,
                data=data,
                tokens=tokens,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        icon='ic_weather_alert',
                        color='#FF5722',
                        sound='default'
                    )
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            alert=messaging.ApsAlert(
                                title=alert.event,
                                body=alert.headline
                            ),
                            sound='default',
                            badge=1
                        )
                    )
                )
            )
            
            # Send notification
            response = messaging.send_multicast(message)
            
            # Log results
            logger.info(f"Successfully sent {response.success_count} notifications")
            
            if response.failure_count > 0:
                logger.warning(f"Failed to send {response.failure_count} notifications")
                
                # Handle invalid tokens
                for idx, resp in enumerate(response.responses):
                    if not resp.success:
                        error_code = resp.exception.code if resp.exception else 'unknown'
                        if error_code in ['registration-token-not-registered', 'invalid-registration-token']:
                            # Remove invalid token
                            user = users_with_tokens[idx]
                            user.firebase_token = None
                            user.save()
                            logger.info(f"Removed invalid token for user {user.id}")
            
        except Exception as e:
            logger.error(f"Error sending FCM notification: {str(e)}")
