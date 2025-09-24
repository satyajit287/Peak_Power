from django.urls import path
from . import views

from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# Custom LogoutView that allows GET
class LogoutAllowGetView(auth_views.LogoutView):
    http_method_names = ['get', 'post', 'head', 'options']
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('workouts/', views.WorkoutListView.as_view(), name='workout_list'),
    path('workouts/<int:pk>/', views.WorkoutDetailView.as_view(), name='workout_detail'),
    path('workouts/new/', views.WorkoutCreateView.as_view(), name='workout_create'),
    path('workouts/<int:pk>/edit/', views.WorkoutUpdateView.as_view(), name='workout_edit'),
    path('workouts/<int:pk>/delete/', views.WorkoutDeleteView.as_view(), name='workout_delete'),
    path('workouts/<int:pk>/like/', views.like_workout, name='workout_like'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', LogoutAllowGetView.as_view(next_page='/'), name='logout'),
    path('accounts/signup/', views.SignUpView.as_view(), name='signup'),
    path('accounts/profile/', views.profile_view, name='profile'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    path('accounts/password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change_form.html'), name='password_change'),
    path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
    path('schedule/', views.weekly_schedule_view, name='weekly_schedule'),
    path('schedule/add/', views.add_schedule_view, name='add_schedule'),
    path('log/', views.log_workout_view, name='log_workout'),
    path('logbook/', views.workout_logbook_view, name='workout_logbook'),
    path('progress/', views.progress_charts_view, name='progress_charts'),
    path('meals/', views.meal_list_view, name='meal_list'),
    path('meals/add/', views.meal_add_view, name='meal_add'),
    path('mealplans/', views.mealplan_list_view, name='mealplan_list'),
    path('mealplans/add/', views.mealplan_add_view, name='mealplan_add'),
    path('workouts/search/', views.workout_search_view, name='workout_search'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
    path('trainers/', views.trainer_list_view, name='trainer_list'),
]
