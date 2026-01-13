import random

from django_ratelimit.decorators import ratelimit
from django.db import IntegrityError, transaction
from django.utils.decorators import method_decorator

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes

import Users.models as user_models
import Shares.models as share_models
from . import serializers as custom_serializer


@ratelimit(key='user', rate='100/m', block=True)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    """
    Retrieve the authenticated user's profile information.
    """

    return Response(
        {
            "status": True,
            "me": custom_serializer.MeSerializer(request.user).data
        }, status=status.HTTP_200_OK
    )


@method_decorator(ratelimit(key='user', rate='100/m', block=True), name='dispatch')
class Targets(APIView):
    """
    API view for managing user-defined stock targets.

    Supports:
    - GET: Retrieve all active (non-deleted) targets for the user
    - POST: Create a new target for a company with buy/sell criteria
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve all active targets for the authenticated user.
        """

        targets = user_models.Targets.objects.filter(user_id=request.user, is_deleted=False)
        serialized = custom_serializer.TargetSerializer(targets, many=True)

        return Response(
            {
                "status": True,
                "targets": serialized.data
            }, status=status.HTTP_200_OK
        )

    def post(self, request):
        """
        Create a new target for a specified company.

        Validates:
        - Company existence
        - Target type (buy or sell)
        - Numeric target amounts and logical range
        - Uniqueness of active target per user, company, and type
        """

        company = (request.data.get('company') or '').strip()

        if not company:
            return Response(
                {
                    "status": False,
                    "message": "Company is required"
                }, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            company = share_models.ListedCompanies.objects.get(name__iexact=company)

        except share_models.ListedCompanies.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "Company not found"
                }, status=status.HTTP_404_NOT_FOUND
            )

        target_type = (request.data.get('target_type') or '').strip().lower()

        if target_type not in ['buy', 'sell']:
            return Response(
                {
                    "status": False,
                    "message": "Target Type must be either buy or sell"
                }, status=status.HTTP_400_BAD_REQUEST
            )

        low_target_amount = request.data.get('low_target') or ''
        high_target_amount = request.data.get('high_target') or ''

        try:
            low_target_amount = float(low_target_amount)
            high_target_amount = float(high_target_amount)

            if low_target_amount >= high_target_amount:
                return Response(
                    {
                        "status": False,
                        "message": "Low Target amount must be less than High Target amount"
                    }, status=status.HTTP_400_BAD_REQUEST
                )

        except (ValueError, TypeError):
            return Response(
                {
                    "status": False,
                    "message": "Low Target amount and High Target amount must be valid numbers"
                }, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                user_models.Targets.objects.create(
                    user_id=request.user,
                    company_id=company,
                    low_target=low_target_amount,
                    high_target=high_target_amount,
                    target_type=target_type
                )

        except IntegrityError:
            return Response(
                {
                    "status": False,
                    "message": "Target for the given company already exists"
                }, status=status.HTTP_409_CONFLICT
            )

        return Response(
            {
                "status": True,
                "message": "Target added"
            }, status=status.HTTP_201_CREATED
        )


@ratelimit(key='ip', rate='100/m', block=True)
@api_view(['GET'])
@permission_classes([AllowAny])
def Testinomials(request):
    testinomials_ids = list(user_models.Testonomials.objects.values_list("id", flat=True))
    random_ids = random.sample(testinomials_ids, k=min(5, len(testinomials_ids)))

    testinomials = user_models.Testonomials.objects.filter(id__in=random_ids)

    return Response(
        {
            "status": True,
            "testinomials": custom_serializer.TestinomialSerializer(testinomials, many=True).data
        }, status=status.HTTP_200_OK
    )


@ratelimit(key='ip', rate='100/m', block=True)
@api_view(['POST'])
@permission_classes([AllowAny])
def Feebacks(request):
    name = request.data.get('name', '').strip().lower()
    email = request.data.get('email', '').strip().lower()
    subject = request.data.get('subject', '').strip().lower()
    message = request.data.get('message', '').strip().lower()

    if not any([name, email, subject, message]):
        return Response(
            {
                'status': False,
                'message': 'All the fields are required'
            }, status=status.HTTP_400_BAD_REQUEST
        )

    return Response(
        {
            "status": True,
            "message": "Message Sent!"
        }, status=status.HTTP_200_OK
    )