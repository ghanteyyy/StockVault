import Users.models as user_models
from django.dispatch import receiver
from django.db.models.signals import pre_save


@receiver(pre_save, sender=user_models.CustomUser)
def set_default_profile_picture(sender, instance, **kwargs):
    """
    Signal receiver function for setting a default profile picture before saving a CustomUser instance.

    This function is connected to the pre-save signal of the CustomUser model. It ensures that a default
    profile picture is set if the user does not provide one before saving.

    Parameters:
        sender (CustomUser): The sender of the signal, expected to be the CustomUser model.
        instance (CustomUser): The instance of the CustomUser being saved.
        **kwargs: Additional keyword arguments passed to the function (not used in this context).
    """

    if not instance.profile_image:
        instance.profile_image = 'default.png'
