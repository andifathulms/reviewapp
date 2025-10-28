from django.db import models
from django.db.models import Avg
from django.contrib.auth.models import User
from django.urls import reverse

from thumbnails.fields import ImageField

from reviewapp.apps.metadata.models import Language, Country, Genre, Creator
from reviewapp.core.utils import FilenameGenerator


class Movie(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    tagline = models.TextField(blank=True)
    synopsis = models.TextField(blank=True)
    image = ImageField(upload_to=FilenameGenerator(prefix='movie_images'), blank=True, null=True)
    genre = models.ManyToManyField(Genre, blank=True)
    director = models.ManyToManyField(Creator, blank=True)
    release_year = models.PositiveIntegerField()
    runtime = models.PositiveIntegerField(help_text="Runtime in minutes")
    language = models.ManyToManyField(Language, blank=True)
    imdb_id = models.CharField(max_length=20, blank=True, null=True, unique=True)
    release_date = models.DateField(blank=True, null=True)
    country = models.ManyToManyField(Country, blank=True)

    class Meta:
        ordering = ['-release_year', 'title']
        indexes = [
            models.Index(fields=['release_year']),
            models.Index(fields=['title']),
        ]

    def __str__(self):
        return f"{self.title} ({self.release_year})"

    def get_absolute_url(self):
        return reverse('movie-detail', kwargs={'slug': self.slug})

    @property
    def average_rating(self):
        return self.reviews.aggregate(avg=Avg('overall_rating'))['avg']


class MovieReview(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    overall_rating = models.FloatField()
    imdb_rating = models.FloatField(blank=True, null=True)
    rottentomatoes_rating = models.FloatField(blank=True, null=True)

    # Main review content
    review_summary = models.TextField(help_text="Brief summary of the review", blank=True, null=True)
    detailed_review = models.TextField(help_text="Full detailed review")
    final_verdict = models.TextField()

    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created']
        unique_together = ['movie', 'created_by']  # One review per user per movie
        indexes = [
            models.Index(fields=['movie', 'created']),
            models.Index(fields=['overall_rating']),
        ]

    def __str__(self):
        return f"{self.movie.title} - {self.overall_rating}/10 by {self.created_by.username}"

    def calculate_weighted_average(self):
        """Calculate weighted average from aspect ratings"""
        aspects = self.aspect_ratings.all()
        if not aspects:
            return self.overall_rating

        total_weight = sum(aspect.category.weight for aspect in aspects)
        weighted_sum = sum(aspect.rating * aspect.category.weight for aspect in aspects)
        return weighted_sum / total_weight if total_weight > 0 else 0


class MovieReviewCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    weight = models.FloatField(default=1.0)

    def __str__(self):
        return self.name


class MovieAspectRating(models.Model):
    review = models.ForeignKey('MovieReview', on_delete=models.CASCADE, related_name='aspect_ratings')
    category = models.ForeignKey('MovieReviewCategory', on_delete=models.CASCADE)
    rating = models.FloatField()
    review_text = models.TextField()

    class Meta:
        unique_together = ['review', 'category']

    def __str__(self):
        return f"{self.review.movie.title} - {self.category.name}: {self.rating}"
