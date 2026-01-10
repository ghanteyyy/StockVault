import os
import uuid
import datetime
import requests
from pathlib import Path
from Users.models import *
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def _create_tags(self):
        BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
        temp_image_path = os.path.join(BASE_DIR, "static", "images", f"{uuid.uuid4().hex}.jpg")

        new_users = []
        number_of_users_to_populate = int(input("Enter the number of users to populate: "))
        fetch_users = requests.get(f'https://randomuser.me/api/?results={number_of_users_to_populate}').json()['results']

        for user in fetch_users:
            email = user['email']
            gender = user['gender']
            name = ' '.join(user['name'].values())
            dob = datetime.datetime.strptime(user['dob']['date'], "%Y-%m-%dT%H:%M:%S.%fZ")

            with open(temp_image_path, 'wb') as img:
                image = requests.get(user['picture']['large']).content
                img.write(image)

            contentfile = ContentFile(image)

            if CustomUser.objects.filter(email=email).exists():
                print(f"User with email {email} already exists. Skipping...")
                continue

            new_user = CustomUser(email=email, name=name, gender=gender, date_of_birth=dob)

            new_user.set_password('root')
            new_user.profile_image.save(temp_image_path, contentfile)
            new_users.append(new_user)

        CustomUser.objects.bulk_create(new_users, ignore_conflicts=True)

    def handle(self, *args, **options):
        self._create_tags()
