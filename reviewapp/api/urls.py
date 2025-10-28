from django.urls import path, include


app_name = "api"

urlpatterns = [
    path('movies/', include('reviewapp.api.movies.urls')),
]
