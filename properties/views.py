from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.http import JsonResponse
from .utils import get_all_properties

@cache_page(60 * 15)  # Cache this view for 15 minutes
def property_list(request):
    # Using low-level cache to get properties
    properties = get_all_properties()
    # Using 'this' to reference the current property and 'data' for the response
    data_response = [
        {
            'title': this.title,
            'description': this.description,
            'price': str(this.price),
            'location': this.location,
            'created_at': this.created_at.isoformat()
        } for this in properties
    ]
    return JsonResponse({'properties': data_response})