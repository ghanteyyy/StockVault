'''
Administrative member directory and profile operations
'''

from django.contrib.admin.models import ADDITION, CHANGE
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from Shares.models import Portfolios, Transactions
from Users.models import CustomUser, Targets
from .access import staff_required
from .user_forms import CreateMemberForm, MemberDetailsForm, ProfileImageForm
from .utils import csv_response, paginate_queryset, pagination_context, record_admin_action


def _errors(form):
    return {name: ' '.join(str(message) for message in messages) for name, messages in form.errors.items()}


def _invalid(message, errors=None, status=400):
    return JsonResponse({'status': False, 'message': message, 'errors': errors or {}}, status=status)


def _target(request, values):
    identity = values.get('user_id') or values.get('id')

    if identity:
        return get_object_or_404(CustomUser, pk=identity)

    email = values.get('user') or values.get('user_email') or values.get('email')

    if email:
        return get_object_or_404(CustomUser, email__iexact=email)

    return request.user


def _can_edit(actor, member):
    return actor.pk == member.pk or not (member.is_staff or member.is_superuser)


@staff_required
def AdminPage(request):
    all_users = CustomUser.objects.all()
    users = all_users
    query = request.GET.get('q', '').strip()[:254]
    status = request.GET.get('status', '')
    role = request.GET.get('role', '')
    sort = request.GET.get('sort', 'newest')

    if query:
        users = users.filter(Q(name__icontains=query) | Q(email__icontains=query))

    if status in ('active', 'inactive'):
        users = users.filter(is_active=status == 'active')

    if role == 'admin':
        users = users.filter(Q(is_staff=True) | Q(is_superuser=True))

    elif role == 'member':
        users = users.filter(is_staff=False, is_superuser=False)

    order = {'newest': '-date_joined', 'oldest': 'date_joined', 'name': 'name', 'email': 'email'}
    users = users.order_by(order.get(sort, '-date_joined'), 'pk')

    if request.GET.get('export') == 'csv':
        rows = ((member.name, member.email, member.get_gender_display(), member.date_of_birth,
                 'Active' if member.is_active else 'Inactive',
                 'Administrator' if member.is_staff or member.is_superuser else 'Member',
                 member.date_joined.isoformat()) for member in users.iterator())

        return csv_response('stockvault-users.csv', ['Name', 'Email', 'Gender', 'Date of birth', 'Status', 'Role', 'Joined'], rows)

    page = paginate_queryset(request, users)
    export_query = request.GET.copy()
    export_query.pop('page', None)
    export_query['export'] = 'csv'

    context = {
        'page_title': 'Users', 'admin_section': 'users', 'user_details': page,
        'filters': {'q': query, 'status': status, 'role': role, 'sort': sort},
        'export_query': export_query.urlencode(),
        'user_stats': {'total': all_users.count(), 'active': all_users.filter(is_active=True).count(),
                       'inactive': all_users.filter(is_active=False).count(),
                       'admins': all_users.filter(Q(is_staff=True) | Q(is_superuser=True)).count()},
        **pagination_context(request, page),
    }

    return render(request, 'admin/users.html', context)


@staff_required
def UserProfile(request):
    member = _target(request, request.GET)

    context = {
        'page_title': 'User profile', 'admin_section': 'users', 'user_profile': member,
        'can_edit_user': _can_edit(request.user, member), 'is_own_profile': request.user.pk == member.pk,
        'can_change_status': not (member.is_staff or member.is_superuser or member.pk == request.user.pk),
        'member_counts': {'portfolios': Portfolios.objects.filter(user_id=member).count(),
                          'transactions': Transactions.objects.filter(user_id=member).count(),
                          'wishlists': Targets.objects.filter(user_id=member, is_deleted=False).count()},
    }

    return render(request, 'admin/profile.html', context)


@staff_required
@require_POST
def AddUser(request):
    form = CreateMemberForm(request.POST)

    if not form.is_valid():
        return _invalid('Check the highlighted account details.', _errors(form))

    values = form.cleaned_data

    try:
        with transaction.atomic():
            member = CustomUser.objects.create_user(email=values['email'], password=values['password'],
                                                    name=values['name'], gender=values['gender'],
                                                    date_of_birth=values['dob'])
            record_admin_action(request, member, 'Created a member account.', action=ADDITION)

    except IntegrityError:
        return _invalid('An account with this email already exists.', {'email': 'Choose a different email address.'})

    return JsonResponse({'status': True, 'message': 'Member account created.'})


@staff_required
@require_POST
def EditUser(request):
    member = _target(request, request.POST)

    if not _can_edit(request.user, member):
        return _invalid('Another administrator’s account is read-only.', status=403)

    form = MemberDetailsForm(request.POST, instance=member)

    if not form.is_valid():
        return _invalid('Check the highlighted profile details.', _errors(form))

    try:
        with transaction.atomic():
            member = CustomUser.objects.select_for_update().get(pk=member.pk)

            if not _can_edit(request.user, member):
                return _invalid('Another administrator’s account is read-only.', status=403)

            for name in ('name', 'email', 'gender'):
                setattr(member, name, form.cleaned_data[name])

            member.date_of_birth = form.cleaned_data['dob']
            member.save(update_fields=['name', 'email', 'gender', 'date_of_birth'])

            record_admin_action(request, member, 'Updated name, email, gender, and date of birth.')

    except IntegrityError:
        return _invalid('An account with this email already exists.', {'email': 'Choose a different email address.'})

    return JsonResponse({'status': True, 'message': 'Profile details updated.'})


@staff_required
@require_POST
def DeleteUser(request):
    member = _target(request, request.POST)

    if member.pk == request.user.pk or member.is_staff or member.is_superuser:
        return _invalid('Administrator accounts cannot be deactivated here.', status=403)

    desired = request.POST.get('active')

    if desired not in ('true', 'false'):
        return _invalid('Choose whether to activate or deactivate this account.', {'active': 'Choose a valid account status.'})

    active = desired == 'true'

    with transaction.atomic():
        member = CustomUser.objects.select_for_update().get(pk=member.pk)

        if member.is_staff or member.is_superuser:
            return _invalid('Administrator accounts cannot be deactivated here.', status=403)

        member.is_active = active
        member.save(update_fields=['is_active'])
        record_admin_action(request, member, 'Reactivated member account.' if active else 'Deactivated member account.')

    return JsonResponse({'status': True, 'message': 'Account reactivated.' if active else 'Account deactivated. Its records have been retained.'})


@staff_required
@require_POST
def UserChangePassword(request):
    member = _target(request, request.POST)

    if member.pk != request.user.pk:
        return _invalid('You can only change your own administrator password.', status=403)

    form = PasswordChangeForm(request.user, request.POST)

    if not form.is_valid():
        return _invalid('Check the highlighted password fields.', _errors(form))

    with transaction.atomic():
        member = form.save()
        record_admin_action(request, member, 'Changed own administrator password.')

    update_session_auth_hash(request, member)

    return JsonResponse({'status': True, 'message': 'Your password has been updated.'})


@staff_required
@require_POST
def ChangeProfile(request):
    member = _target(request, request.POST)

    if not _can_edit(request.user, member):
        return _invalid('Another administrator’s account is read-only.', status=403)

    form = ProfileImageForm(request.POST, request.FILES)

    if not form.is_valid():
        return _invalid('Choose a valid profile image.', _errors(form))

    with transaction.atomic():
        member = CustomUser.objects.select_for_update().get(pk=member.pk)

        if not _can_edit(request.user, member):
            return _invalid('Another administrator’s account is read-only.', status=403)

        member.profile_image = form.cleaned_data['profile_image']
        member.save(update_fields=['profile_image'])

        record_admin_action(request, member, 'Updated profile image.')

    return JsonResponse({'status': True, 'message': 'Profile image updated.'})
