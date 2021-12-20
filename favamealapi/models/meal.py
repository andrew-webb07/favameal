from django.db import models
from .mealrating import MealRating


class Meal(models.Model):

    name = models.CharField(max_length=55)
    restaurant = models.ForeignKey("Restaurant", on_delete=models.CASCADE)

    # TODO: Add an user_rating custom properties

    @property
    def user_rating(self):
        return self.__user_rating
    
    @user_rating.setter
    def user_rating(self, value):
        self.__user_rating = value

    # TODO: Add an avg_rating custom properties

    @property
    def avg_rating(self):
        """Average rating calculated attribute for each meal"""
        ratings = MealRating.objects.filter(meal=self)

        total_rating = 0
        for rating in ratings:
            total_rating += rating.rating
        
        if total_rating == 0:
            return 0
        else:
            avg_rating = total_rating / len(ratings)
            return avg_rating