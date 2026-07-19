import pytest
from django.contrib.auth.models import User

@pytest.fixture
def create_superuser(db):
    """Create a superuser for testing. Depends on db fixture to ensure migrations are applied."""
    print()
    print("=== creating superuser for a test ===")
    test_superuser = User.objects.create_superuser(
        username='test_superuser',
        email='test@example.com',
        password='pass1234'
    )

    if test_superuser is not None:
        print(f'=== created test-superuser with id {test_superuser.id} ===')
    else:
        print('=== ERROR: test-superuser is not created ===')
    
    yield test_superuser


