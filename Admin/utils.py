'''
Small helpers for paginated, auditable administration views
'''

import csv
from decimal import Decimal

from django.contrib.admin.models import CHANGE, LogEntry
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.http import HttpResponse


def paginate_queryset(request, queryset, per_page=20):
    try:
        requested = int(request.GET.get('per_page', per_page))

    except (TypeError, ValueError):
        requested = per_page

    return Paginator(queryset, requested if requested in (20, 50, 100) else per_page).get_page(request.GET.get('page'))


def pagination_context(request, page):
    query = request.GET.copy()

    for key in ('page', 'export'):
        query.pop(key, None)

    return {'page_obj': page, 'query_string': query.urlencode()}


def csv_response(filename, headers, rows):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response['Cache-Control'] = 'no-store'
    response.write('\ufeff')
    writer = csv.writer(response)

    def safe_cell(value):
        if value is None:
            return ''

        if isinstance(value, (int, float, Decimal)):
            return value

        text = str(value)

        return "'" + text if text.lstrip().startswith(('=', '+', '-', '@')) else text

    writer.writerow(headers)

    for row in rows:
        writer.writerow([safe_cell(value) for value in row])

    return response


def record_admin_action(request, obj, message, action=CHANGE):
    return LogEntry.objects.create(
        user_id=request.user.pk,
        content_type=ContentType.objects.get_for_model(obj, for_concrete_model=False),
        object_id=str(obj.pk), object_repr=(getattr(obj, 'question', None) or str(obj))[:200],
        action_flag=action, change_message=message,
    )
