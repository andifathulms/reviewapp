from django.contrib import admin

from .models import Book, BookReview, ReviewSection, ReviewSectionType

admin.site.register(Book)
admin.site.register(BookReview)
admin.site.register(ReviewSectionType)
admin.site.register(ReviewSection)
