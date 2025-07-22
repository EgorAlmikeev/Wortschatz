from django.db import models
from django.contrib.auth.models import User
from .utils import get_superuser_id

class OwnedModelMixin(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="%(class)s_owner",
        db_index=True,
        default=get_superuser_id
    )

    class Meta:
        abstract = True