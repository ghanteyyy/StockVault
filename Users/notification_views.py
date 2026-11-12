import json

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST, require_safe

from .models import Notification


FEED_LIMIT = 20
MAX_NOTIFICATION_ID = 2**63 - 1


def _access_error(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Sign in to view notifications.'}, status=401)
    if request.user.is_staff:
        return JsonResponse({'error': 'Notifications are available in the member workspace.'}, status=403)
    return None


@never_cache
@require_safe
def notification_feed(request):
    error = _access_error(request)
    if error is not None:
        return error

    notifications = Notification.objects.filter(user=request.user)
    items = [
        {
            'id': item.id,
            'title': item.title,
            'detail': item.detail,
            'created_at': item.created_at.isoformat(),
            'unread': item.read_at is None,
        }
        for item in notifications[:FEED_LIMIT]
    ]
    return JsonResponse({
        'unread_count': notifications.filter(read_at__isnull=True).count(),
        'items': items,
    })


@never_cache
@require_POST
def mark_notifications_read(request):
    error = _access_error(request)
    if error is not None:
        return error

    try:
        payload = json.loads(request.body)
    except (ValueError, RecursionError):
        payload = None
    through_id = payload.get('through_id') if isinstance(payload, dict) else None
    if type(through_id) is not int or not 0 < through_id <= MAX_NOTIFICATION_ID:
        return JsonResponse({'error': 'Choose a valid notification.'}, status=400)

    notifications = Notification.objects.filter(user=request.user)
    if not notifications.filter(pk=through_id).exists():
        return JsonResponse({'error': 'Notification not found.'}, status=404)

    unread = notifications.filter(read_at__isnull=True)
    unread.filter(pk__lte=through_id).update(read_at=timezone.now())
    return JsonResponse({'unread_count': unread.count()})
