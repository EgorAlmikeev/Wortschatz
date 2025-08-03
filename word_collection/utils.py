from django.contrib.auth.models import User

def get_superuser_id():
    super_users = User.objects.filter(is_superuser=True)
    return super_users.first() if super_users.exists() else None