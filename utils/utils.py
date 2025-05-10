import uuid
import random


def generate_uuid_hex():
    '''
    Generates a unique value (e.g., for filenames, IDs)
    '''

    random_values = list(f'{uuid.uuid4().hex}{uuid.uuid4()}')
    random.shuffle(random_values)

    return ''.join(random_values)


def user_profile_path(instance, filename):
    '''
    Generate the file path for uploading profile image.

    The uploaded file will be stored in the following format:
        MEDIA_ROOT/<user-id>/profile/<unique_id>.<extension>
    '''

    extension = filename.split('.')[-1]
    new_file_name = f'{generate_uuid_hex()}.{extension}'

    return f'{instance.id}/"profile"/{new_file_name}'
