from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

from model_utils.choices import Choices
from thumbnails.fields import ImageField

from reviewapp.core.utils import FilenameGenerator


class Book(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(max_length=255, unique=True)
    isbn = models.CharField(max_length=13, unique=True, blank=True, null=True)
    image = ImageField(upload_to=FilenameGenerator(prefix='book_images'), blank=True, null=True)
    authors = models.ManyToManyField('BookAuthor', blank=True)
    publisher = models.CharField(max_length=100, blank=True)
    publication_year = models.PositiveIntegerField()
    publication_date = models.DateField(blank=True, null=True)
    pages = models.PositiveIntegerField(blank=True, null=True)
    category = models.ManyToManyField('BookCategory', blank=True)
    summary = models.TextField(blank=True)
    language = models.CharField(max_length=50, blank=True, default="English")

    class Meta:
        ordering = ['-publication_date', 'title']
        indexes = [
            models.Index(fields=['publication_year']),
            models.Index(fields=['title']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('book-detail', kwargs={'slug': self.slug})

    @property
    def display_authors(self):
        return ", ".join([author.name for author in self.authors.all()])

    @property
    def display_categories(self):
        return ", ".join([category.name for category in self.category.all()])


class BookReview(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    overall_rating = models.FloatField()
    goodreads_rating = models.FloatField(blank=True, null=True)
    amazon_rating = models.FloatField(blank=True, null=True)

    # Main review content
    review_summary = models.TextField(help_text="Brief summary of the review", blank=True, null=True)
    detailed_review = models.TextField(help_text="Full detailed review")
    personal_reflection = models.TextField(help_text="Personal thoughts and reflections", blank=True)
    final_verdict = models.TextField()

    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='book_reviews')
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"{self.book.title} - {self.overall_rating}/10 by {self.created_by.username}"

    class Meta:
        ordering = ['-created']
        unique_together = ['book', 'created_by']  # One review per user per book
        indexes = [
            models.Index(fields=['book', 'created']),
            models.Index(fields=['overall_rating']),
        ]
        verbose_name = "Book Review"
        verbose_name_plural = "Book Reviews"

    def __str__(self):
        return f"{self.book.title} - {self.overall_rating}/10 by {self.created_by.username}"

    def get_absolute_url(self):
        return reverse('bookreview-detail', kwargs={'pk': self.pk})


class ReviewSectionType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon_name = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    SUGGESTED_GENRES = Choices(
        (1, 'ALL', 'All Genres'),
        (2, 'FICTION', 'Fiction'),
        (3, 'NON_FICTION', 'Non-Fiction'),
        (4, 'ACADEMIC', 'Academic'),
        (5, 'SELF_HELP', 'Self-Help'),
        (6, 'HISTORY', 'History'),
        (7, 'RELIGIOUS', 'Religious'),
        (8, 'SCIENCE', 'Science'),
        (9, 'BIOGRAPHY', 'Biography'),
        (10, 'TECHNICAL', 'Technical'),
    )
    suggested_for = models.PositiveSmallIntegerField(choices=SUGGESTED_GENRES, default='ALL')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ReviewSection(models.Model):
    review = models.ForeignKey('BookReview', on_delete=models.CASCADE, related_name='sections')
    section_type = models.ForeignKey(ReviewSectionType, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True)  # for numbering review section like key ideas
    content = models.TextField()
    quote_title = models.CharField(max_length=200, blank=True, null=True)  # for quotes
    icon_name = models.CharField(max_length=50, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.review.book.title} - {self.section_type.name}"


class BookAuthor(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(blank=True, null=True)
    photo = ImageField(upload_to=FilenameGenerator(prefix='author_photos'), blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Book Author"
        verbose_name_plural = "Book Authors"

    def __str__(self):
        return self.name


class BookCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Book Category"
        verbose_name_plural = "Book Categories"

    def __str__(self):
        return self.name
