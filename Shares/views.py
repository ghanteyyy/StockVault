from django.db import transaction
from django.core.cache import cache
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from utils import calculator
import Shares.models as share_models
from . import serializers as custom_serializer
from utils import helpers


@ratelimit(key='user', rate='100/m', block=True)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def NepseIndices(request):
    """
    Retrieve NEPSE index history
    """

    cache_key = f"nepse:indices:v1:user:{request.user.id}"
    cache_value = cache.get(cache_key)

    if cache_value is not None:
        return Response(
            {
                "status": True,
                "data": cache_value
            }, status=status.HTTP_200_OK
        )

    nepse_indices_qs = (share_models.NepseIndices.objects
                    .using('stockmarketdata')
                    .order_by('date'))
    serialized = custom_serializer.NepseIndicesSerializer(nepse_indices_qs, many=True)

    cache.set(cache_key, serialized.data, timeout=60)

    return Response(
        {
            "status": True,
            "data": serialized.data
        }, status=status.HTTP_200_OK
    )


@ratelimit(key='ip', rate='100/m', block=True)
def ListedCompanies(request):
    """
    Retrieve all listed companies
    """

    companies = share_models.ListedCompanies.objects.all()
    serialized = custom_serializer.ListedCompaniesSerializer(companies, many=True)

    return Response(
        {
            "status": True,
            "companies": serialized.data
        }, status=status.HTTP_200_OK
    )


@method_decorator(ratelimit(key='user', rate='100/m', block=True), name='dispatch')
class Portfolio(APIView):
    """
    API view for managing a user's stock portfolio.

    Supports:
    - GET: Retrieve user's portfolio
    - POST: Add or update stock holdings
    - DELETE: Remove a stock holding

    All operations are rate-limited per user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve the authenticated user's portfolio.
        """

        portfolios = share_models.Portfolios.objects.filter(user_id=request.user)
        serialized = custom_serializer.PortfolioSerializer(portfolios, many=True)

        return Response(
            {
                "status": True,
                "portfolios": serialized.data
            }, status=status.HTTP_200_OK
        )

    def post(self, request):
        """
        Add shares to the user's portfolio or update an existing holding.

        If the stock already exists in the portfolio, the share count
        and total cost are incremented atomically to prevent race conditions.

        Validates:
        - Company existence
        - Share quantity and buying rate
        - Buy type (IPO or Secondary)
        """

        company = helpers.get_company_or_error(request)

        if isinstance(company, Response):
            return company

        try:
            share_quantity = int(request.data.get('share_quantity'))
            buying_rate = float(request.data.get('buying_rate'))

            if share_quantity <= 0 or buying_rate <= 0:
                return Response(
                    {
                        "status": False,
                        "message": "Share quantity and buying rate must be greater than 0"
                    }, status=status.HTTP_400_BAD_REQUEST
                )

        except (ValueError, TypeError):
            return Response(
                {
                    "status": False,
                    "message": "Share quantity and buying rate must be valid numeric values"
                }, status=status.HTTP_400_BAD_REQUEST
            )

        buy_type = (request.data.get('buy_type') or '').strip().lower()

        if buy_type not in ['ipo', 'secondary']:
            return Response(
                {
                    "status": False,
                    "message": "Buy type must be IPO or Secondary"
                }, status=status.HTTP_400_BAD_REQUEST
            )

        stock = calculator.buy_shares_calculation(share_quantity, buying_rate, buy_type)
        total_cost = round(stock['total_amount'], 2)

        with transaction.atomic():
            try:
                portfolio = (
                    share_models.Portfolios.objects
                    .select_for_update()
                    .get(user_id=request.user, company_id=company)
                    )

                portfolio.total_cost += total_cost
                portfolio.number_of_shares += share_quantity
                portfolio.save()

                created = False

            except share_models.Portfolios.DoesNotExist:
                portfolio = share_models.Portfolios.objects.create(
                    user_id=request.user,
                    company_id=company,
                    total_cost=total_cost,
                    number_of_shares=share_quantity
                )

                created = True

        return Response(
            {
                "status": True,
                "portfolio": custom_serializer.PortfolioSerializer(portfolio).data
            }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    def delete(self, request):
        """
        Remove a stock holding from the user's portfolio.
        """

        company = helpers.get_company_or_error(request)

        if isinstance(company, Response):
            return company

        try:
            portfolio = share_models.Portfolios.objects.get(user_id=request.user, company_id=company)
            portfolio.delete()

            return Response(
                {
                    "status": True,
                    "message": "Stock holding deleted"
                }, status=status.HTTP_200_OK
            )

        except share_models.Portfolios.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "No stock holdings found for the specified company"
                }, status=status.HTTP_404_NOT_FOUND
            )


@method_decorator(ratelimit(key='user', rate='100/m', block=True), name='dispatch')
class Wishlist(APIView):
    """
    API view for managing the user's stock wishlist.

    Supports:
    - GET: Retrieve wishlist
    - POST: Add a company to wishlist
    - DELETE: Remove a company from wishlist
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve the authenticated user's wishlist.
        """

        wishlists = share_models.WishLists.objects.filter(user_id=request.user)
        serialized = custom_serializer.WishlistSerializer(wishlists, many=True)

        return Response(
            {
                "status": True,
                "wishlists": serialized.data
            }, status=status.HTTP_200_OK
        )

    def post(self, request):
        """
        Add a company to the user's wishlist.

        Prevents duplicate wishlistentries for the same company.
        """

        company = helpers.get_company_or_error(request)

        if isinstance(company, Response):
            return company

        wishlist, created = share_models.WishLists.objects.get_or_create(user_id=request.user, company_id=company)

        if created:
            return Response(
                {
                    "status": True,
                    "message": "Wishlist added"

                }, status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "status": False,
                "message": "Wishlist exists"

            }, status=status.HTTP_409_CONFLICT
        )

    def delete(self, request):
        """
        Remove a company from the user's wishlist.
        """

        company = helpers.get_company_or_error(request)

        if isinstance(company, Response):
            return company

        try:
            wishlist = share_models.WishLists.objects.get(user_id=request.user, company_id=company)
            wishlist.delete()

            return Response(
                {
                    "status": True,
                    "message": "Wishlist deleted"
                }, status=status.HTTP_200_OK
            )

        except share_models.WishLists.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "Wishlist not found"
                }, status=status.HTTP_404_NOT_FOUND
            )