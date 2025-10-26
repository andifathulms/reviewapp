from django.db import models
from django.contrib.auth.models import User

from thumbnails.fields import ImageField

from reviewapp.core.utils import FilenameGenerator


class Movie(models.Model):
    title = models.CharField(max_length=200)
    tagline = models.TextField(blank=True)
    synopsis = models.TextField(blank=True)
    image = ImageField(upload_to=FilenameGenerator(prefix='movie_images'), blank=True, null=True)
    genre = models.ManyToManyField('MovieGenre', blank=True)
    director = models.ManyToManyField('MovieDirector', blank=True)
    release_year = models.PositiveIntegerField()
    runtime = models.PositiveIntegerField(help_text="Runtime in minutes")
    language = models.ManyToManyField('MovieLanguage', blank=True)
    imdb_id = models.CharField(max_length=20, blank=True, null=True, unique=True)
    release_date = models.DateField(blank=True, null=True)
    country = models.ManyToManyField('MovieCountry', blank=True)

    class Meta:
        ordering = ['-release_year', 'title']
        indexes = [
            models.Index(fields=['release_year']),
            models.Index(fields=['title']),
        ]

    def __str__(self):
        return f"{self.title} ({self.release_year})"

    @property
    def average_rating(self):
        if hasattr(self, 'review'):
            return self.review.rating
        return None


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


class MovieGenre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class MovieDirector(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(blank=True, null=True)
    photo = ImageField(upload_to=FilenameGenerator(prefix='director_photos'), blank=True, null=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class MovieLanguage(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, blank=True, help_text="ISO language code")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class MovieCountry(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=5, blank=True, help_text="ISO country code")

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Movie countries"

    def __str__(self):
        return self.name
