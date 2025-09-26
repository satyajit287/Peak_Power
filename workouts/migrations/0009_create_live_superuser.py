from django.db import migrations
from django.contrib.auth import get_user_model

def create_superuser(apps, schema_editor):
    User = get_user_model()

    # --- CHANGE YOUR NEW ADMIN DETAILS HERE ---
    # Replace 'admin_user' with the username you want.
    # Replace the email with your email.
    # Replace the password with a strong password.
    if not User.objects.filter(username='admin_user').exists():
        User.objects.create_superuser(
            username='satyajit28',
            email='satyajitmojar44@gmail.com',
            password='satya2802'
        )

class Migration(migrations.Migration):

    dependencies = [
        # This is based on your screenshot showing 0008_trainer.py was the last one.
        ('workouts', '0008_trainer'), 
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]