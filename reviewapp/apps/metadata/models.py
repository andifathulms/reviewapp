from django.db import models

from model_utils.choices import Choices
from thumbnails.fields import ImageField

from reviewapp.core.utils import FilenameGenerator


class Language(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, blank=True, help_text="ISO language code")

    def __str__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=5, blank=True, help_text="ISO country code")

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    TYPE = Choices(
        (1, 'MOVIE', 'Movie'),
        (2, 'BOOK', 'Book'),
    )
    type = models.PositiveSmallIntegerField(choices=TYPE)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name + " (" + self.get_TYPE_display() + ")"


class Creator(models.Model):
    name = models.CharField(max_length=100)
    TYPE = Choices(
        (1, 'Director', 'Director'),
        (2, 'Author', 'Author'),
    )
    type = models.PositiveSmallIntegerField(choices=TYPE)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(blank=True, null=True)
    photo = ImageField(upload_to=FilenameGenerator(prefix='creators'), blank=True, null=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name + " (" + self.get_TYPE_display() + ")"
