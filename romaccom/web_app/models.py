from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
import re

GLASGOW_POSTCODES = ["G1", "G2", "G3", "G4", "G5", "G11", "G12", "G13", "G14", "G15", "G20", "G21", "G22", "G23", "G31", "G32", "G33", "G34", "G40", "G41", "G42", "G43", "G44", "G45", "G46", "G51", "G52", "G53", "G61", "G62", "G64", "G65", "G66", "G67", "G68", "G69", "G70"]

"""
 Validates that postcode that is being tried to added to an accomodation is valid
 """
def validate_glasgow_postcode(value):
    if not any(value == pc for pc in GLASGOW_POSTCODES):
        raise ValidationError(f"{value} is not a valid Glasgow postcode. Use only the first part (e.g., G1, G2, G12)")

"""
 Validates that the address that is being tried to added to an accomodation is valid
 """
def validate_uk_address(value):
    if not re.match(r'^\d+\s[A-Za-z\s]+$', value):  # e.g.: "123 Main Street"
        raise ValidationError("Address must start with a number followed by a street name.")

"""
Custom user model with account type and profile visibility fields
"""
class User(AbstractUser):
    ACCOUNT_TYPES = [
        ('private', 'Private'),
        ('public', 'Public'),
    ]

    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPES, default='public')
    profile_visibility = models.BooleanField(default=True)

    def __str__(self):
        return self.username

"""
User profile model with website and profile picture
"""
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

"""
Model representing an operator managing accommodations
"""
class Operator(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
"""
Profile for an operator, including a business description, website, and logo
"""
class OperatorProfile(models.Model):
    operator = models.OneToOneField(Operator, on_delete=models.CASCADE, related_name="profile")
    description = models.TextField(blank=True, help_text="Tell people about your business")
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to="operator_logos/", blank=True)

    def __str__(self):
        return f"{self.operator.name}'s Profile"

"""
Model representing an accommodation with 
name, address, postcode, embeddded google maps link, operator,rating, view count and description
"""
class Accommodation(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255, validators=[validate_uk_address])
    postcode = models.CharField(max_length=10, validators=[validate_glasgow_postcode])
    map_link = models.URLField(max_length=500, blank=True)
    operators = models.ManyToManyField(Operator, related_name='accommodations')
    average_rating = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    view_count = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)

    """
    Updates the average rating based on related reviews
    """
    def update_average_rating(self):
        reviews = self.reviews.all()
        self.average_rating = sum(r.rating for r in reviews) / reviews.count() if reviews.count() > 0 else 0
        self.save()

    """
    Increments the view count for the accomm
    """
    def increment_view_count(self):
        self.view_count += 1
        self.save()

    def __str__(self):
        return self.name

"""
Model for user reviews on accommodations
"""
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE, related_name='reviews')
    title = models.CharField(max_length=255, blank=True, help_text="Optional review title")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  

    """
    Overrides save method to update accommodation's average rating after saving
    """
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.accommodation.update_average_rating()

    def __str__(self):
        return f"Review by {self.user.username} on {self.accommodation.name}"

"""
Model to associate images with reviews
"""
class Image(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='review_images/', default='default.jpg')

    def __str__(self):
        return f"Image for Review {self.review.id}"

"""
Model to store images of accommodations
"""
class AccommodationImage(models.Model):
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='accommodation_images/', default='default.jpg')
    is_main = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Image for {self.accommodation.name}"
