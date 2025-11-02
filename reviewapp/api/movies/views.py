from django.http import JsonResponse, Http404
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from reviewapp.apps.movies.models import Movie
from reviewapp.core.serializers import serialize_movie
from reviewapp.core.querysets import movies_queryset_for_serialization


@method_decorator(csrf_exempt, name="dispatch")
class Index(View):
    """
    GET /api/movies
    Optional query params:
      - verbose=true
      - include_reviews=true
      - include_aspects=true
      - limit=<number> (limit results)
    """

    def get(self, request):
        verbose = request.GET.get("verbose", "false").lower() == "true"
        include_reviews = request.GET.get("include_reviews", "false").lower() == "true"
        include_aspects = request.GET.get("include_aspects", "false").lower() == "true"
        limit = request.GET.get("limit")

        qs = movies_queryset_for_serialization(Movie.objects.all())
        if limit and limit.isdigit():
            qs = qs[:int(limit)]

        data = [
            serialize_movie(
                movie,
                verbose=verbose,
                include_reviews=include_reviews,
                include_aspects=include_aspects,
            )
            for movie in qs
        ]
        return JsonResponse(data, safe=False, json_dumps_params={"ensure_ascii": False})


@method_decorator(csrf_exempt, name="dispatch")
class Details(View):
    """
    GET /api/movies/<slug>/
    Optional query params:
      - verbose=true
      - include_reviews=true
      - include_aspects=true
      - reviews_limit=<number>
    """

    def get(self, request, slug):
        try:
            movie = movies_queryset_for_serialization(
                Movie.objects.filter(slug=slug)
            ).get(slug=slug)
        except Movie.DoesNotExist:
            raise Http404("Movie not found")

        verbose = request.GET.get("verbose", "true").lower() == "true"
        include_reviews = request.GET.get("include_reviews", "true").lower() == "true"
        include_aspects = request.GET.get("include_aspects", "true").lower() == "true"
        reviews_limit = request.GET.get("reviews_limit")

        reviews_limit = int(reviews_limit) if (reviews_limit and reviews_limit.isdigit()) else 5

        data = serialize_movie(
            movie,
            verbose=True,
            include_reviews=True,
            include_aspects=True,
            reviews_limit=reviews_limit,
        )
        return JsonResponse(data, safe=False, json_dumps_params={"ensure_ascii": False})
