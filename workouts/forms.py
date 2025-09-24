
from django import forms
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Workout, Profile, WorkoutSchedule, WorkoutLog, WorkoutSetLog, Meal, MealPlan

# Custom signup form with avatar
class CustomSignUpForm(UserCreationForm):
    avatar = forms.ImageField(required=False)
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields

class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ['title','description','difficulty','type','body_part','duration_minutes','exercises','image']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio','avatar','fitness_goals','height_cm','weight_kg']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'profile-form-input', 'rows': 3, 'placeholder': 'Tell us about yourself...'}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'profile-form-input'}),
            'fitness_goals': forms.Textarea(attrs={'class': 'profile-form-input', 'rows': 3, 'placeholder': 'Your fitness goals...'}),
            'height_cm': forms.NumberInput(attrs={'class': 'profile-form-input', 'placeholder': 'Height (cm)'}),
            'weight_kg': forms.NumberInput(attrs={'class': 'profile-form-input', 'placeholder': 'Weight (kg)'}),
        }

class WorkoutScheduleForm(forms.ModelForm):
    class Meta:
        model = WorkoutSchedule
        fields = ['day', 'workout', 'note']

class WorkoutLogForm(forms.ModelForm):
    class Meta:
        model = WorkoutLog
        fields = ['workout', 'completed', 'notes', 'duration']

class WorkoutSetLogForm(forms.ModelForm):
    class Meta:
        model = WorkoutSetLog
        fields = ['exercise', 'set_number', 'reps', 'weight']

class MealForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = ['name', 'calories', 'protein', 'carbs', 'fat', 'date', 'notes']

class MealPlanForm(forms.ModelForm):
    class Meta:
        from django import forms
        from django.contrib.auth.forms import UserCreationForm
        from .models import Workout, Profile, WorkoutSchedule, WorkoutLog, WorkoutSetLog, Meal, MealPlan
        model = MealPlan
        fields = ['date', 'meals', 'notes']
