from django.urls import path

from reviewapp.api.movies.views import Index, Details


app_name = "movies"

urlpatterns = [
    path("", Index.as_view(), name="index"),
    path("<slug:slug>/", Details.as_view(), name="details"),
]
