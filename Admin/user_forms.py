'''
Validated, deliberately limited forms for administrative member management
'''

import warnings

from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from PIL import Image, UnidentifiedImageError

from Users.models import CustomUser


class MemberDetailsForm(forms.Form):
    name = forms.CharField(min_length=3, max_length=100)
    email = forms.EmailField(max_length=254)
    gender = forms.ChoiceField(choices=CustomUser._meta.get_field('gender').choices)
    dob = forms.DateField(required=False, input_formats=['%Y-%m-%d'])

    def __init__(self, *args, instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = instance

    def clean_email(self):
        email = self.cleaned_data['email']
        existing = CustomUser.objects.filter(email__iexact=email)

        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)

        if existing.exists():
            raise ValidationError('An account with this email already exists.')

        return email

    def clean_dob(self):
        birth = self.cleaned_data['dob']

        if birth:
            today = timezone.localdate()
            age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))

            if not 13 <= age <= 110:
                raise ValidationError('Choose a date of birth for an age between 13 and 110.')

        return birth


class CreateMemberForm(MemberDetailsForm):
    password = forms.CharField(strip=False)

    def clean(self):
        values = super().clean()

        if values.get('password'):
            candidate = CustomUser(name=values.get('name', ''), email=values.get('email', ''))

            try:
                validate_password(values['password'], user=candidate)

            except ValidationError as error:
                self.add_error('password', error)

        return values


class ProfileImageForm(forms.Form):
    profile_image = forms.FileField()

    def clean_profile_image(self):
        uploaded = self.cleaned_data['profile_image']

        if uploaded.size > 5 * 1024 * 1024:
            raise ValidationError('Choose an image no larger than 5 MB.')

        if not uploaded.name.lower().endswith(('.jpg', '.jpeg', '.png')):
            raise ValidationError('Choose a JPG or PNG image.')

        try:
            with warnings.catch_warnings():
                warnings.simplefilter('error', Image.DecompressionBombWarning)
                image = Image.open(uploaded)

                if image.format not in ('JPEG', 'PNG'):
                    raise ValidationError('Choose a valid JPG or PNG image.')
                image.verify()

        except (UnidentifiedImageError, OSError, ValueError, SyntaxError, Image.DecompressionBombError, Image.DecompressionBombWarning):
            raise ValidationError('This file could not be read as an image.')

        finally:
            uploaded.seek(0)

        return uploaded
