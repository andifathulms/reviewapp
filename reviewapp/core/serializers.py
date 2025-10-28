from django.utils.timezone import localtime

from reviewapp.apps.books.models import Book, BookReview, ReviewSection
from reviewapp.apps.movies.models import Movie, MovieReview, MovieAspectRating
from reviewapp.apps.metadata.models import Genre, Creator, Language, Country

from typing import Optional


def serialize_movie(movie: Movie, *, verbose: bool = False, include_reviews: bool = False,
                    include_aspects: bool = False, reviews_limit: Optional[int] = 5) -> dict:
    genres = movie.genre.all()
    directors = movie.director.all()
    languages = movie.language.all()
    countries = movie.country.all()

    payload = {
        'id': movie.id,
        'title': movie.title,
        'slug': movie.slug,
        'tagline': movie.tagline,
        'synopsis': movie.synopsis,
        'image': movie.image.url if getattr(movie, "image", None) else None,
        'genres': [serialize_genre(g) for g in genres],
        'director': [serialize_creator(d) for d in directors],
        'release_year': movie.release_year,
        'runtime': movie.runtime,
        'language': [serialize_language(l) for l in languages],
        'imdb_id': movie.imdb_id,
        'release_date': movie.release_date,
        'country': [serialize_country(c) for c in countries],
    }

    if verbose or include_reviews:
        # assume public reviews only in API; adjust filter if admins can see non-public
        qs = movie.reviews.filter(is_public=True).order_by('-created')

        if verbose:
            latest = qs.first()
            payload["reviews_summary"] = {
                "count": qs.count(),
                "average_rating": movie.average_rating,
                "latest_review": serialize_movie_review(latest) if latest else None,
            }

        if include_reviews:
            if reviews_limit is not None:
                qs = qs[:reviews_limit]
            payload["reviews"] = [serialize_movie_review(r, include_aspects=include_aspects) for r in qs]

    return payload


def serialize_genre(genre: Genre) -> dict:
    return {
        'id': genre.id,
        'name': genre.name,
        'type': genre.type,
        'description': genre.description,
    }


def serialize_language(language: Language) -> dict:
    return {
        'id': language.id,
        'name': language.name,
        'code': language.code,
    }


def serialize_country(country: Country) -> dict:
    return {
        'id': country.id,
        'name': country.name,
        'code': country.code,
    }


def serialize_creator(creator: Creator) -> dict:
    return {
        'id': creator.id,
        'name': creator.name,
        'type': creator.type,
        'bio': creator.bio,
        'birth_date': creator.birth_date,
        'photo': creator.photo.url if creator.photo else None,
    }


def serialize_aspect_rating(ar: MovieAspectRating) -> dict:
    return {
        "category": {
            "id": ar.category.id,
            "name": ar.category.name,
            "weight": ar.category.weight,
        },
        "rating": ar.rating,
        "review_text": ar.review_text,
    }

def serialize_movie_review(review: MovieReview, include_aspects: bool = False) -> dict:
    data = {
        "id": review.id,
        "overall_rating": review.overall_rating,
        "imdb_rating": review.imdb_rating,
        "rottentomatoes_rating": review.rottentomatoes_rating,
        "weighted_average": review.calculate_weighted_average(),
        "review_summary": review.review_summary,
        "detailed_review": review.detailed_review,
        "final_verdict": review.final_verdict,
        "created_by": {
            "id": review.created_by.id,
            "username": review.created_by.username,
        },
        "created": localtime(review.created).isoformat(),
        "updated": localtime(review.updated).isoformat(),
        "is_public": review.is_public,
    }
    if include_aspects:
        # relies on prefetch of aspect_ratings + category for efficiency
        data["aspect_ratings"] = [serialize_aspect_rating(ar) for ar in review.aspect_ratings.all()]
    return data


def serialize_book_review_section_type(rst: ReviewSectionType) -> dict:
    return {
        "id": rst.id,
        "name": rst.name,
        "description": rst.description,
        "icon_name": rst.icon_name,
        "is_active": rst.is_active,
        "suggested_for": rst.get_suggested_for_display(),  # human-readable label
    }

def serialize_book_review_section(sec: ReviewSection) -> dict:
    return {
        "id": sec.id,
        "section_type": serialize_book_review_section_type(sec.section_type),
        "title": sec.title,
        "content": sec.content,
        "quote_title": sec.quote_title,
        "icon_name": sec.icon_name,
        "order": sec.order,
    }

def serialize_book_review(review: BookReview, include_sections: bool = True) -> dict:
    data = {
        "id": review.id,
        "overall_rating": review.overall_rating,
        "goodreads_rating": review.goodreads_rating,
        "amazon_rating": review.amazon_rating,
        "review_summary": review.review_summary,
        "detailed_review": review.detailed_review,
        "personal_reflection": review.personal_reflection,
        "final_verdict": review.final_verdict,
        "created_by": {"id": review.created_by.id, "username": review.created_by.username},
        "created": localtime(review.created).isoformat(),
        "updated": localtime(review.updated).isoformat(),
        "is_public": review.is_public,
        "url": review.get_absolute_url() if hasattr(review, "get_absolute_url") else None,
    }
    if include_sections:
        data["sections"] = [serialize_book_review_section(s) for s in review.sections.all()]
    return data


def serialize_book(book: Book, *, verbose: bool = False, include_reviews: bool = False,
                   include_sections: bool = True, reviews_limit: Optional[int] = 5) -> dict:
    authors = book.authors.all()
    categories = book.category.all()
    languages = book.language.all()
    countries = book.country.all()

    payload = {
        "id": book.id,
        "title": book.title,
        "subtitle": book.subtitle,
        "slug": book.slug,
        "isbn": book.isbn,
        "image": book.image.url if getattr(book, "image", None) else None,
        "authors": [serialize_creator(a) for a in authors],
        "publisher": book.publisher,
        "publication_year": book.publication_year,
        "publication_date": book.publication_date,
        "pages": book.pages,
        "category": [serialize_genre(g) for g in categories],
        "summary": book.summary,
        "language": [serialize_language(l) for l in languages],
        "country": [serialize_country(c) for c in countries],
        "url": book.get_absolute_url() if hasattr(book, "get_absolute_url") else None,
        # handy display strings from your model properties:
        "display_authors": book.display_authors,
        "display_categories": book.display_categories,
    }

    if verbose or include_reviews:
        public_reviews_qs = book.reviews.filter(is_public=True).order_by("-created")

        if verbose:
            payload["reviews_summary"] = {
                "count": public_reviews_qs.count(),
                "average_rating": public_reviews_qs.aggregate(avg=Avg("overall_rating"))["avg"],
                "latest_review": serialize_book_review(public_reviews_qs.first(), include_sections=False)
                if public_reviews_qs.exists() else None,
            }

        if include_reviews:
            qs = public_reviews_qs
            if reviews_limit is not None:
                qs = qs[:reviews_limit]
            payload["reviews"] = [serialize_book_review(r, include_sections=include_sections) for r in qs]

    return payload
