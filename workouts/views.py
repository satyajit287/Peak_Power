from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from collections import defaultdict
import json
from django.db.models import Sum, Count, Q
from datetime import timedelta

from .models import Workout, Profile, WorkoutSchedule, WorkoutLog, WorkoutSetLog, Meal, MealPlan, Badge, UserBadge, Streak
from .models import Trainer
from .forms import WorkoutForm, ProfileForm, WorkoutScheduleForm, WorkoutLogForm, WorkoutSetLogForm, MealForm, MealPlanForm, CustomSignUpForm

class WorkoutListView(ListView):
    model = Workout
    template_name = 'workouts/list.html'
    context_object_name = 'workouts'
    ordering = ['-created_at']

class WorkoutDetailView(DetailView):
    model = Workout
    template_name = 'workouts/detail.html'

class WorkoutCreateView(LoginRequiredMixin, CreateView):
    model = Workout
    form_class = WorkoutForm
    template_name = 'workouts/form.html'
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class WorkoutUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Workout
    form_class = WorkoutForm
    template_name = 'workouts/form.html'
    def test_func(self):
        return self.get_object().author == self.request.user

class WorkoutDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Workout
    template_name = 'workouts/confirm_delete.html'
    success_url = reverse_lazy('workout_list')
    def test_func(self):
        return self.get_object().author == self.request.user

def like_workout(request, pk):
    if request.method == 'POST':
        w = get_object_or_404(Workout, pk=pk)
        w.likes += 1
        w.save()
        return JsonResponse({'likes': w.likes})
    return JsonResponse({'error':'POST required'}, status=400)

class SignUpView(CreateView):
    form_class = CustomSignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('workout_list')
    def form_valid(self, form):
        user = form.save()
        # Save avatar to profile
        avatar = form.cleaned_data.get('avatar')
        if avatar:
            user.profile.avatar = avatar
            user.profile.save()
        login(self.request, user)
        return redirect(self.success_url)

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user.profile)
    badges = UserBadge.objects.filter(user=request.user)
    streak = getattr(request.user, 'streak', None)
    return render(request, 'registration/profile.html', {'form': form, 'badges': badges, 'streak': streak})

@login_required
def weekly_schedule_view(request):
    days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    schedule = defaultdict(list)
    user_schedules = WorkoutSchedule.objects.filter(user=request.user)
    for s in user_schedules:
        schedule[s.day].append(s)
    return render(request, 'workouts/weekly_schedule.html', {'schedule': schedule, 'days': days})

@login_required
def add_schedule_view(request):
    if request.method == 'POST':
        form = WorkoutScheduleForm(request.POST)
        if form.is_valid():
            sched = form.save(commit=False)
            sched.user = request.user
            sched.save()
            return redirect('weekly_schedule')
    else:
        form = WorkoutScheduleForm()
    return render(request, 'workouts/schedule_form.html', {'form': form})

@login_required
def log_workout_view(request):
    if request.method == 'POST':
        form = WorkoutLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            log.save()
            # --- Gamification logic ---
            profile = request.user.profile
            profile.points += 10  # 10 points per workout
            profile.save()
            # Streaks
            from datetime import timedelta
            from django.utils import timezone
            today = timezone.now().date()
            streak, _ = Streak.objects.get_or_create(user=request.user)
            if streak.last_completed == today - timedelta(days=1):
                streak.current_streak += 1
            elif streak.last_completed != today:
                streak.current_streak = 1
            streak.last_completed = today
            if streak.current_streak > streak.longest_streak:
                streak.longest_streak = streak.current_streak
            streak.save()
            # Badges
            if streak.current_streak == 7:
                badge, _ = Badge.objects.get_or_create(name='7-Day Streak', defaults={'description':'Logged 7 days in a row!','icon':'🔥'})
                UserBadge.objects.get_or_create(user=request.user, badge=badge)
            if profile.points >= 100:
                badge, _ = Badge.objects.get_or_create(name='100 Points', defaults={'description':'Earned 100 points!','icon':'🏅'})
                UserBadge.objects.get_or_create(user=request.user, badge=badge)
            return redirect('workout_logbook')
    else:
        form = WorkoutLogForm()
    return render(request, 'workouts/log_form.html', {'form': form})

@login_required
def workout_logbook_view(request):
    logs = WorkoutLog.objects.filter(user=request.user).order_by('-date')
    return render(request, 'workouts/logbook.html', {'logs': logs})

@login_required
def dashboard_view(request):
    from .models import Workout, WorkoutSchedule, WorkoutLog
    stats = {
        'workouts': Workout.objects.filter(author=request.user).count(),
        'scheduled': WorkoutSchedule.objects.filter(user=request.user).count(),
        'completed': WorkoutLog.objects.filter(user=request.user, completed=True).count(),
    }
    return render(request, 'dashboard.html', {'stats': stats})

@login_required
def progress_charts_view(request):
    from .models import WorkoutLog, WorkoutSetLog
    from django.utils import timezone
    today = timezone.now().date()
    # Frequency: count of workouts per week (last 4 weeks)
    freq_labels = []
    freq_counts = []
    for i in range(4, 0, -1):
        week_start = today - timedelta(days=i*7)
        week_end = week_start + timedelta(days=6)
        freq_labels.append(f"{week_start.strftime('%b %d')}")
        count = WorkoutLog.objects.filter(user=request.user, date__range=(week_start, week_end), completed=True).count()
        freq_counts.append(count)
    freq_data = json.dumps({
        'labels': freq_labels,
        'datasets': [{
            'label': 'Workouts',
            'data': freq_counts,
            'backgroundColor': '#4e79a7',
        }]
    })
    # Weight lifted: sum of weights per log (last 10 logs)
    logs = WorkoutLog.objects.filter(user=request.user, completed=True).order_by('-date')[:10][::-1]
    weight_labels = [l.date.strftime('%b %d') for l in logs]
    weight_data_points = []
    for l in logs:
        total_weight = WorkoutSetLog.objects.filter(log=l).aggregate(total=Sum('weight'))['total'] or 0
        weight_data_points.append(total_weight)
    weight_data = json.dumps({
        'labels': weight_labels,
        'datasets': [{
            'label': 'Weight (kg)',
            'data': weight_data_points,
            'borderColor': '#f28e2b',
            'fill': False,
        }]
    })
    # Calories burned (estimate: 5 cal/min * duration)
    cal_labels = [l.date.strftime('%b %d') for l in logs]
    cal_data_points = [l.duration * 5 for l in logs]
    cal_data = json.dumps({
        'labels': cal_labels,
        'datasets': [{
            'label': 'Calories',
            'data': cal_data_points,
            'borderColor': '#e15759',
            'fill': False,
        }]
    })
    return render(request, 'progress_charts.html', {
        'freq_data': freq_data,
        'weight_data': weight_data,
        'cal_data': cal_data,
    })

@login_required
def meal_list_view(request):
    meals = Meal.objects.filter(user=request.user).order_by('-date')
    return render(request, 'meals/list.html', {'meals': meals})

@login_required
def meal_add_view(request):
    if request.method == 'POST':
        form = MealForm(request.POST)
        if form.is_valid():
            meal = form.save(commit=False)
            meal.user = request.user
            meal.save()
            return redirect('meal_list')
    else:
        form = MealForm()
    return render(request, 'meals/form.html', {'form': form})

@login_required
def mealplan_list_view(request):
    plans = MealPlan.objects.filter(user=request.user).order_by('-date')
    return render(request, 'meals/plan_list.html', {'plans': plans})

@login_required
def mealplan_add_view(request):
    if request.method == 'POST':
        form = MealPlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.user = request.user
            plan.save()
            form.save_m2m()
            return redirect('mealplan_list')
    else:
        form = MealPlanForm()
    return render(request, 'meals/plan_form.html', {'form': form})

# --- Workout search/filter ---
@login_required
def workout_search_view(request):
    qs = Workout.objects.all()
    q = request.GET.get('q','')
    difficulty = request.GET.get('difficulty','')
    body_part = request.GET.get('body_part','')
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
    if difficulty:
        qs = qs.filter(difficulty=difficulty)
    if body_part:
        qs = qs.filter(body_part=body_part)
    return render(request, 'workouts/search.html', {
        'workouts': qs,
        'q': q,
        'difficulty': difficulty,
        'body_part': body_part,
    })

from django.contrib.auth.models import User

@login_required
def leaderboard_view(request):
    from .models import Profile, Streak
    top_points = Profile.objects.order_by('-points')[:10]
    top_streaks = Streak.objects.order_by('-current_streak')[:10]
    return render(request, 'leaderboard.html', {
        'top_points': top_points,
        'top_streaks': top_streaks,
    })


def trainer_list_view(request):
    """Public view: list available trainers."""
    trainers = Trainer.objects.filter(active=True).order_by('name')
    return render(request, 'trainers/list.html', {'trainers': trainers})
