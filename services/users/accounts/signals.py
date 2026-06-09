from logging import getLogger

from django.db.models.signals import post_save
from django.dispatch import receiver

from .events import UserRegisteredEvent, UserUpdateEvent
from .models import User, UserProfile
from .publisher import publish_history_event

logger = getLogger(__name__)


@receiver(post_save, sender=User)
def on_user_save(sender, instance, created, **kwargs):
    logger.info("USER SAVE TRIGGERED!!")
    if created:
        # Dispatch the event to the history service
        logger.info("User registered: %s", instance.username)
        event = UserRegisteredEvent(
            user_id=str(instance.id), email=instance.email, username=instance.username
        )

        publish_history_event.delay(event.to_dict())


@receiver(post_save, sender=UserProfile)
def on_user_profile_saved(sender, instance, created, **kwargs):
    if not created:
        event = UserUpdateEvent(
            user_id=str(instance.user.id),
            email=instance.user.email,
            updated_fields= list(instance.get_dirty_fields().keys()),
        )
        publish_history_event.delay(event.to_dict())
