from django.urls import path

from reviewapp.apps.movies.views import Index, Details


app_name = "movies"

urlpatterns = [
    path("api/movies/", Index.as_view(), name="index"),
    path("api/movies/<slug:slug>/", Details.as_view(), name="details"),
]
