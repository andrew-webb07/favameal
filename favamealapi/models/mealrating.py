from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

class MealRating(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="mealrating")
    meal = models.ForeignKey("Meal", on_delete=models.CASCADE, related_name="mealrating")
    rating = models.IntegerField(default=1, validators=[MaxValueValidator(10), MinValueValidator(1)])