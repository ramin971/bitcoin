from .indicators import calculate_indicators
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def bitcoin_indicators(request):
    data = calculate_indicators()
    return Response(data)
