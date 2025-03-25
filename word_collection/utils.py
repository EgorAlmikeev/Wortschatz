from django.contrib.auth.models import User

def get_superuser_id():
    return User.objects.filter(is_superuser=True).first().id
