"""View module for handling requests about meals"""
from django.core.exceptions import ValidationError
from django.http import HttpResponseServerError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from favamealapi.models import Meal, MealRating, Restaurant, FavoriteMeal, favoritemeal
from django.contrib.auth.models import User
from favamealapi.views.restaurant import RestaurantSerializer
from django.db.models import Q


class MealView(ViewSet):
    """ViewSet for handling meal requests"""

    def create(self, request):
        """Handle POST operations for meals

        Returns:
            Response -- JSON serialized meal instance
        """
        meal = Meal()
        meal.name = request.data["name"]
        meal.restaurant = Restaurant.objects.get(pk=request.data["restaurant_id"])

        try:
            meal.save()
            serializer = MealSerializer(
                meal, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as ex:
            return Response({"reason": ex.message}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single meal

        Returns:
            Response -- JSON serialized meal instance
        """
        try:
            meal = Meal.objects.get(pk=pk)

            # TODO: Get the rating for current user and assign to `user_rating` property
            mealRating = MealRating.objects.get(user=request.auth.user)
            meal.user_rating = mealRating.rating

            # TODO: Get the average rating for requested meal and assign to `avg_rating` property

            # TODO: Assign a value to the `is_favorite` property of requested meal


            serializer = MealSerializer(
                meal, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def list(self, request):
        """Handle GET requests to meals resource

        Returns:
            Response -- JSON serialized list of meals
        """
        meals = Meal.objects.all()

        # TODO: Get the rating for current user and assign to `user_rating` property

        # TODO: Get the average rating for each meal and assign to `avg_rating` property

        # TODO: Assign a value to the `is_favorite` property of each meal

        serializer = MealSerializer(
            meals, many=True, context={'request': request})

        return Response(serializer.data)

    # TODO: Add a custom action named `rate` that will allow a client to send a
    #  POST and a PUT request to /meals/3/rate with a body of..
    #       {
    #           "rating": 3
    #       }




    # TODO: Add a custom action named `star` that will allow a client to send a
    #  POST and a DELETE request to /meals/3/star.
    
    @action(methods=['post', 'delete'], detail=True)
    def star(self, request, pk):
        if request.method == "POST":
            meal = Meal.objects.get(pk=pk)
            user = User.objects.get(username=request.auth.user.username)
            favorite_meal = FavoriteMeal()
            favorite_meal.user = user
            favorite_meal.meal = meal
            try:
                favorite_meal.save()
                serializer = FavoriteMealSerializer(favorite_meal, many=False, context={'request': request})
                return Response(serializer.data)
            except Exception as ex:
                return Response({'message': ex.args[0]})
            
        elif request.method == "DELETE":
            meal = Meal.objects.get(pk=pk)
            user = User.objects.get(username=request.auth.user.username)
            favorite_meal = FavoriteMeal.objects.filter(Q(meal=meal) & Q(user=user))
            try:
                favorite_meal.delete()
                return Response({}, status=status.HTTP_204_NO_CONTENT)
            except Exception as ex:
                return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserSerializer(serializers.ModelSerializer):
    """JSON serializer for event organizer's related Django user"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class MealRatingSerializer(serializers.ModelSerializer):
    """JSON serializer for event organizer"""
    user = UserSerializer(many=False)

    class Meta:
        model = MealRating
        fields = ['user', 'meal', 'rating']

class MealSerializer(serializers.ModelSerializer):
    """JSON serializer for meals"""
    restaurant = RestaurantSerializer(many=False)

    class Meta:
        model = Meal
        fields = ('id', 'name', 'restaurant', 'user_rating')
        depth = 1
        
class FavoriteMealSerializer(serializers.ModelSerializer):
    """JSON serializer for favorites"""

    class Meta:
        model = FavoriteMeal
        fields = ('__all__')
        depth = 1