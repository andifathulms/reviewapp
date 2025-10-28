from django.contrib import admin

from .models import Movie, MovieReview, MovieAspectRating, MovieReviewCategory

admin.site.register(Movie)
admin.site.register(MovieReview)
admin.site.register(MovieAspectRating)
admin.site.register(MovieReviewCategory)
