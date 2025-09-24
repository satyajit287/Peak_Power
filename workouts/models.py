from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Exercise(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    def __str__(self): return self.name

class Workout(models.Model):
    DIFFICULTY = [('Easy','Easy'),('Medium','Medium'),('Hard','Hard')]
    TYPE = [
        ('Cardio', 'Cardio'),
        ('Strength', 'Strength'),
        ('Flexibility', 'Flexibility'),
        ('Balance', 'Balance'),
        ('Other', 'Other'),
    ]
    BODY_PARTS = [
        ('Full Body', 'Full Body'),
        ('Chest', 'Chest'),
        ('Back', 'Back'),
        ('Legs', 'Legs'),
        ('Arms', 'Arms'),
        ('Shoulders', 'Shoulders'),
        ('Core', 'Core'),
        ('Other', 'Other'),
    ]
    title = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workouts')
    description = models.TextField(blank=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY, default='Easy')
    type = models.CharField(max_length=20, choices=TYPE, default='Other')
    body_part = models.CharField(max_length=20, choices=BODY_PARTS, default='Full Body')
    duration_minutes = models.PositiveIntegerField(default=20)
    exercises = models.ManyToManyField(Exercise, blank=True)
    image = models.ImageField(upload_to='workouts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.PositiveIntegerField(default=0)
    def __str__(self): return self.title

# --- Meal/Diet Plan ---
class Meal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meals')
    name = models.CharField(max_length=100)
    calories = models.PositiveIntegerField(default=0)
    protein = models.FloatField(default=0)
    carbs = models.FloatField(default=0)
    fat = models.FloatField(default=0)
    date = models.DateField()
    notes = models.TextField(blank=True)
    def __str__(self):
        return f"{self.name} ({self.date})"

class MealPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mealplans')
    date = models.DateField()
    meals = models.ManyToManyField(Meal, blank=True)
    notes = models.TextField(blank=True)
    def __str__(self):
        return f"Meal Plan {self.date} for {self.user.username}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    fitness_goals = models.TextField(blank=True)
    height_cm = models.PositiveIntegerField(blank=True, null=True, help_text="Height in centimeters")
    weight_kg = models.PositiveIntegerField(blank=True, null=True, help_text="Weight in kilograms")
    points = models.PositiveIntegerField(default=0)
    def __str__(self): return f"{self.user.username} Profile"

# --- Gamification ---
class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True, help_text='Icon class or emoji')
    def __str__(self):
        return self.name

class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    date_awarded = models.DateField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"

class Streak(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='streak')
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_completed = models.DateField(null=True, blank=True)
    def __str__(self):
        return f"{self.user.username} Streak: {self.current_streak}"


# --- Workout Planner/Scheduler ---
class WorkoutSchedule(models.Model):
    DAYS = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='schedules')
    day = models.CharField(max_length=10, choices=DAYS)
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='scheduled_for')
    note = models.CharField(max_length=255, blank=True)
    class Meta:
        unique_together = ('user', 'day', 'workout')
    def __str__(self):
        return f"{self.user.username} - {self.day}: {self.workout.title}"

# --- Progress Tracking / Workout Logbook ---
class WorkoutLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_logs')
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='logs')
    date = models.DateField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    duration = models.PositiveIntegerField(default=0, help_text='Duration in minutes')
    def __str__(self):
        return f"{self.user.username} - {self.workout.title} on {self.date}"

class WorkoutSetLog(models.Model):
    log = models.ForeignKey(WorkoutLog, on_delete=models.CASCADE, related_name='sets')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    set_number = models.PositiveIntegerField()
    reps = models.PositiveIntegerField()
    weight = models.FloatField(null=True, blank=True, help_text='Weight in kg')
    def __str__(self):
        return f"{self.log} | {self.exercise.name} Set {self.set_number}: {self.reps} reps @ {self.weight or 0}kg"


class Trainer(models.Model):
    """Represent a coach/trainer available to users."""
    name = models.CharField(max_length=120)
    bio = models.TextField(blank=True)
    specialties = models.CharField(max_length=255, blank=True, help_text='Comma separated specialties')
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    photo = models.ImageField(upload_to='trainers/', blank=True, null=True)
    active = models.BooleanField(default=True, help_text='Is this trainer currently available?')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-active','name']

    def __str__(self):
        return self.name

@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()
