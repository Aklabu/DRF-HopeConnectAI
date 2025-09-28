import json
import logging
import time
from firebase_admin import messaging
from django.conf import settings
from django.utils import timezone
from accounts.models import CustomUser

logger = logging.getLogger(__name__)


class FCMNotificationService:
    """
    Service class to handle Firebase Cloud Messaging notifications
    """
    
    @staticmethod
    def _check_firebase_availability():
        """
        Check if Firebase is available and properly configured
        """
        try:
            from firebase_admin import _apps
            return bool(_apps) and getattr(settings, 'FIREBASE_AVAILABLE', False)
        except ImportError:
            logger.error("Firebase Admin SDK not installed")
            return False
    
    @staticmethod
    def send_alert_notification(alert):
        """
        Send push notification for a new weather alert
        """
        if not FCMNotificationService._check_firebase_availability():
            logger.warning("Firebase not available - skipping alert notification")
            return False
            
        try:
            # Get all users with firebase tokens who want weather alerts
            users_with_tokens = CustomUser.objects.filter(
                firebase_token__isnull=False,
                receive_weather_alerts=True
            ).exclude(firebase_token='')
            
            if not users_with_tokens.exists():
                logger.info("No users with firebase tokens found for weather alerts")
                return False
            
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
            
            # Send notification - use send_all for batch messaging
            try:
                # Try the newer send_all method first
                response = messaging.send_all([
                    messaging.Message(
                        notification=notification,
                        data=data,
                        token=token,
                        android=message.android,
                        apns=message.apns
                    ) for token in tokens
                ])
                
                # Log results
                logger.info(f"Successfully sent {response.success_count} alert notifications")
                
                if response.failure_count > 0:
                    logger.warning(f"Failed to send {response.failure_count} alert notifications")
                    
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
                
                return response.success_count > 0
                
            except AttributeError:
                # Fallback to individual send calls for older SDK versions
                logger.info("Using individual send calls as fallback")
                success_count = 0
                
                for idx, token in enumerate(tokens):
                    try:
                        individual_message = messaging.Message(
                            notification=notification,
                            data=data,
                            token=token,
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
                        
                        response = messaging.send(individual_message)
                        success_count += 1
                        
                    except messaging.UnregisteredError:
                        logger.warning(f"Invalid token for user {users_with_tokens[idx].id}")
                        users_with_tokens[idx].firebase_token = None
                        users_with_tokens[idx].save()
                    except Exception as e:
                        logger.error(f"Failed to send to token {idx}: {str(e)}")
                
                logger.info(f"Individual sends completed: {success_count}/{len(tokens)} successful")
                return success_count > 0
            
        except ImportError as e:
            logger.error(f"Firebase messaging module not available: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error sending FCM alert notification: {str(e)}")
            return False
    
    @staticmethod
    def send_test_notification(user, title, body):
        """
        Send a test push notification to a specific user
        """
        if not FCMNotificationService._check_firebase_availability():
            logger.warning("Firebase not available - skipping test notification")
            return False
            
        if not user.firebase_token:
            logger.warning(f"User {user.id} has no Firebase token")
            return False
            
        try:
            # Create notification payload
            notification = messaging.Notification(
                title=title,
                body=body
            )
            
            # Create data payload
            data = {
                'user_id': str(user.id),
                'type': 'test_notification',
                'timestamp': str(int(timezone.now().timestamp()))
            }
            
            # Create message for single device
            message = messaging.Message(
                notification=notification,
                data=data,
                token=user.firebase_token,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        icon='ic_notification',
                        color='#2196F3',
                        sound='default'
                    )
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            alert=messaging.ApsAlert(
                                title=title,
                                body=body
                            ),
                            sound='default',
                            badge=1
                        )
                    )
                )
            )
            
            # Send notification
            response = messaging.send(message)
            
            logger.info(f"Successfully sent test notification to user {user.id}. Message ID: {response}")
            return True
            
        except messaging.UnregisteredError:
            logger.warning(f"Invalid Firebase token for user {user.id}")
            # Remove invalid token
            user.firebase_token = None
            user.save()
            return False
        except ImportError as e:
            logger.error(f"Firebase messaging module not available: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error sending test notification to user {user.id}: {str(e)}")
            return False
    
    @staticmethod
    def send_bulk_notification(users, title, body, data=None):
        """
        Send notification to multiple users
        """
        if not FCMNotificationService._check_firebase_availability():
            logger.warning("Firebase not available - skipping bulk notification")
            return False
            
        try:
            # Filter users with valid tokens
            users_with_tokens = [user for user in users if user.firebase_token]
            
            if not users_with_tokens:
                logger.info("No users with firebase tokens found for bulk notification")
                return False
            
            # Extract tokens
            tokens = [user.firebase_token for user in users_with_tokens]
            
            # Create notification payload
            notification = messaging.Notification(
                title=title,
                body=body
            )
            
            # Create data payload
            notification_data = data or {}
            notification_data.update({
                'type': 'bulk_notification',
                'timestamp': str(int(time.time()))
            })
            
            # Create multicast message
            message = messaging.MulticastMessage(
                notification=notification,
                data=notification_data,
                tokens=tokens,
                android=messaging.AndroidConfig(
                    priority='normal',
                    notification=messaging.AndroidNotification(
                        icon='ic_notification',
                        color='#2196F3',
                        sound='default'
                    )
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            alert=messaging.ApsAlert(
                                title=title,
                                body=body
                            ),
                            sound='default'
                        )
                    )
                )
            )
            
            # Send notification
            response = messaging.send_multicast(message)
            
            logger.info(f"Successfully sent {response.success_count} bulk notifications")
            
            # Handle failures
            if response.failure_count > 0:
                logger.warning(f"Failed to send {response.failure_count} bulk notifications")
                
                for idx, resp in enumerate(response.responses):
                    if not resp.success:
                        error_code = resp.exception.code if resp.exception else 'unknown'
                        if error_code in ['registration-token-not-registered', 'invalid-registration-token']:
                            user = users_with_tokens[idx]
                            user.firebase_token = None
                            user.save()
                            logger.info(f"Removed invalid token for user {user.id}")
            
            return response.success_count > 0
            
        except ImportError as e:
            logger.error(f"Firebase messaging module not available: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error sending bulk notification: {str(e)}")
            return False