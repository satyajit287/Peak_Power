from rest_framework import serializers
from .models import Workout
class WorkoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workout
        fields = ['id','title','description','difficulty','duration_minutes','likes','image']
