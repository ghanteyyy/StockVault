from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from utils import utils


class CustomUserManager(BaseUserManager):
    '''
    Define a model manager for User model with no username field
    '''

    def _create_user(self, email, password=None, **extra_fields):
        '''
        Create and save a User with the given email and password
        '''

        if not email:
            raise ValueError('The given email must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password=None, **extra_fields):

        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        '''
        Create and save a SuperUser with the given email and password
        '''

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    '''
    Custom user model representing an individual user.
    '''
    # --- Authentication Fields ---
    username = None
    email = models.EmailField(
                verbose_name=_('email address'),
                unique=True,
                error_messages={
                    "unique": _("A user with this email already exists."),
                }
            )

    id = models.CharField(primary_key=True, editable=False, default=utils.generate_uuid_hex, max_length=255)

    # --- User Details ---
    name = models.CharField(
                verbose_name=_("full name"),
                max_length=100, null=False, blank=False
            )

    gender = models.CharField(
                verbose_name=_('gender'),
                max_length=6, null=False, blank=False,
                choices=[
                    ("male", _("Male")),
                    ("female", _("Female")),
                    ("others", _("Others")),
                ]
            )

    date_of_birth = models.DateField(
                        verbose_name=_('date of birth'),
                        null=True, blank=True
                    )

    profile_image = models.ImageField(
                        verbose_name=_('profile image'),
                        blank=True, null=True, max_length=255,
                        upload_to=utils.user_profile_path
                    )

    # --- Auth Settings ---
    USERNAME_FIELD = 'email'  # Use email for auth
    REQUIRED_FIELDS = []  # No additional required fields

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return self.email


class RecentActivities(models.Model):
    id = models.CharField(primary_key=True, editable=False, default=utils.generate_uuid_hex, max_length=255)
    user_id = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE)

    activity = models.TextField(editable=False)
    recorded_at = models.DateTimeField(editable=False, default=now)
