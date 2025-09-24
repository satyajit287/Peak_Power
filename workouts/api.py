from rest_framework import generics
from .models import Workout
from .serializers import WorkoutSerializer

class WorkoutListAPI(generics.ListCreateAPIView):
    queryset = Workout.objects.all().order_by('-created_at')
    serializer_class = WorkoutSerializer

class WorkoutDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer
