from django.urls import path
from .api import WorkoutListAPI, WorkoutDetailAPI

urlpatterns = [
    path('workouts/', WorkoutListAPI.as_view()),
    path('workouts/<int:pk>/', WorkoutDetailAPI.as_view()),
]
