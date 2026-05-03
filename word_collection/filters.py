import django_filters
from .models import Word


class WordFilter(django_filters.FilterSet):
    part_of_speech_id = django_filters.NumberFilter()
    created_date_time = django_filters.DateFromToRangeFilter()
    definition = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Word
        fields = ["part_of_speech_id", "created_date_time"]
