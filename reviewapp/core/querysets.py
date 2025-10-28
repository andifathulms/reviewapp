from django.db.models import Prefetch

from reviewapp.apps.books.models import Book, BookReview, ReviewSection
from reviewapp.apps.movies.models import Movie, MovieReview, MovieAspectRating

from typing import Iterable


def books_queryset_for_serialization(base_qs=None) -> Iterable[Book]:
    """
    Use this in your views before serializing:
        qs = books_queryset_for_serialization(Book.objects.all())
        data = [serialize_book(b, verbose=True, include_reviews=True) for b in qs]
    """
    if base_qs is None:
        base_qs = Book.objects.all()

    return (
        base_qs
        .prefetch_related(
            "authors", "category", "language", "country",
            Prefetch(
                "reviews",
                queryset=(
                    BookReview.objects.filter(is_public=True)
                    .select_related("created_by", "book")
                    .prefetch_related(
                        Prefetch(
                            "sections",
                            queryset=ReviewSection.objects.select_related("section_type")
                        )
                    )
                ),
            ),
        )
    )


def movies_queryset_for_serialization(base_qs=None) -> Iterable[Movie]:
    """
    Use this in your views before serializing:
        qs = movies_queryset_for_serialization(Movie.objects.all())
        data = [serialize_movie(m, verbose=True, include_reviews=True, include_aspects=True) for m in qs]
    """
    if base_qs is None:
        base_qs = Movie.objects.all()

    return (
        base_qs
        .prefetch_related(
            "genre",
            "director",
            "language",
            "country",
            Prefetch(
                "reviews",
                queryset=(
                    MovieReview.objects.filter(is_public=True)
                    .select_related("created_by", "movie")
                    .prefetch_related(
                        Prefetch(
                            "aspect_ratings",
                            queryset=MovieAspectRating.objects.select_related("category")
                        )
                    )
                    .order_by("-created")
                ),
            ),
        )
    )