from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('workouts.urls')),
    path('api/', include('workouts.api_urls')),
    path('', RedirectView.as_view(pattern_name='workout_list', permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
