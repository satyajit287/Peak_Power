from django.contrib import admin
from .models import Exercise, Workout, Profile, Trainer


@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
	list_display = ('name', 'email', 'phone', 'active')
	list_filter = ('active',)
	search_fields = ('name', 'specialties', 'email')

admin.site.register(Exercise)
admin.site.register(Workout)
admin.site.register(Profile)
