from rest_framework import status
from rest_framework.response import Response
import Shares.models as share_models


def get_company_or_error(request):
        """
        Retrieve a company object from the request or return an error response.

        Reads the company name from request data, validates its presence,
        and attempts to fetch the corresponding ListedCompanies record.
        """

        company_name = (request.data.get('company') or '').strip()

        if not company_name:
            return Response(
                 {
                      "status": False,
                      "message": "Company is required"
                 }, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            return share_models.ListedCompanies.objects.get(name__iexact=company_name)

        except share_models.ListedCompanies.DoesNotExist:
            return Response(
                 {
                      "status": False,
                      "message": "Company not found"
                 }, status=status.HTTP_404_NOT_FOUND
            )
