"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from catalog.views import (
    artist_detail,
    city_list,
    event_detail,
    event_list,
    venue_detail,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("users.urls")),
    path("api/", include("users.been_urls")),
    path("api/cities/", city_list, name="city-list"),
    path("api/events/", event_list, name="event-list"),
    path("api/events/<int:event_id>/", event_detail, name="event-detail"),
    path("api/venues/<int:venue_id>/", venue_detail, name="venue-detail"),
    path("api/artists/<int:artist_id>/", artist_detail, name="artist-detail"),
]
