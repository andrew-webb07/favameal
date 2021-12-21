"""View module for handling requests about restaurants"""
from django.core.exceptions import ValidationError
from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from favamealapi.models import Restaurant
from favamealapi.models import favoriterestaurant
from favamealapi.models.favoriterestaurant import FavoriteRestaurant
from django.contrib.auth.models import User 
from rest_framework.decorators import action
from django.db.models import Q


class RestaurantView(ViewSet):
    """ViewSet for handling restuarant requests"""

    def create(self, request):
        """Handle POST operations for restaurants

        Returns:
            Response -- JSON serialized event instance
        """
        rest = Restaurant()
        rest.name = request.data["name"]
        rest.address = request.data["address"]

        try:
            rest.save()
            serializer = RestaurantSerializer(
                rest, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as ex:
            return Response({"reason": ex.message}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single event

        Returns:
            Response -- JSON serialized game instance
        """
        try:
            restaurant = Restaurant.objects.get(pk=pk)

            # TODO: Add the correct value to the `favorite` property of the requested restaurant
            user = User.objects.get(username=request.auth.user.username)
            favorite = FavoriteRestaurant.objects.filter(Q(user=user) & Q(restaurant=restaurant))
            
            if favorite:
                restaurant.favorite = True
            else:
                restaurant.favorite = False

            serializer = RestaurantSerializer(
                restaurant, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def list(self, request):
        """Handle GET requests to restaurants resource

        Returns:
            Response -- JSON serialized list of restaurants
        """
        restaurants = Restaurant.objects.all()

        # TODO: Add the correct value to the `favorite` property of each restaurant
        user = User.objects.get(username=request.auth.user.username)
        user_favorites = FavoriteRestaurant.objects.filter(user=user)
        
        for restaurant in restaurants:
            for favorite in user_favorites:
                if restaurant.id == favorite.restaurant_id:
                    restaurant.favorite = True
                    break
                else:
                    restaurant.favorite = False 
                

        serializer = RestaurantSerializer(restaurants, many=True, context={'request': request})

        return Response(serializer.data)

    # TODO: Write a custom action named `star` that will allow a client to
    # send a POST and a DELETE request to /restaurant/2/star
    
    @action(methods=['post', 'delete'], detail=True)
    def star(self, request, pk=None):
        if request.method == 'POST':
            restaurant = Restaurant.objects.get(pk=pk)
            user = User.objects.get(username=request.auth.user.username)
            # restaurant.favorite = True
            favorite_restaurant = FavoriteRestaurant()
            favorite_restaurant.user = user
            favorite_restaurant.restaurant = restaurant
            try:
                favorite_restaurant.save()
                serializer = FaveSerializer(favorite_restaurant, many=False, context={'request': request})
                return Response(serializer.data)
            except Exception as ex:
                return Response({'message': ex.args[0]})
        elif request.method == "DELETE":
            try:
                restaurant = Restaurant.objects.get(pk=pk)
                user = User.objects.get(username=request.auth.user.username)
                favorite = FavoriteRestaurant.objects.filter(Q(user=user) & Q(restaurant=restaurant))
                # restaurant.favorite = False
                favorite.delete()
                return Response({}, status=status.HTTP_204_NO_CONTENT)
            except Exception as ex:
                return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RestaurantSerializer(serializers.ModelSerializer):
    """JSON serializer for restaurants"""

    class Meta:
        model = Restaurant
        fields = ('id', 'name', 'address', 'favorite',)

class FaveSerializer(serializers.ModelSerializer):
    """JSON serializer for favorites"""

    class Meta:
        model = FavoriteRestaurant
        fields = ('__all__')
        depth = 1