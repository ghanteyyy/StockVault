import json
from django.http import JsonResponse
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url


def GenerateCaptcha(request=None):
    key = CaptchaStore.generate_key()

    return JsonResponse({'captcha_key': key, 'captcha_image_url': captcha_image_url(key)})


def VerifyCaptcha(request):
    if request.method.lower() == 'post':
        hashkey = request.POST.get('captcha_0')

        user_answer = (request.POST.get('captcha_1') or "").strip()
        valid_captcha = CaptchaStore.objects.filter(hashkey=hashkey, response__iexact=user_answer).exists()

        if valid_captcha:
            return JsonResponse({'status': valid_captcha, 'message': 'Captcha verified'})

        new_captcha = GenerateCaptcha()

        return JsonResponse({'status': valid_captcha, 'message': 'Captcha didn\'t matched ', **new_captcha})

    return JsonResponse({'status': False, 'message': 'POST method was expected'})
