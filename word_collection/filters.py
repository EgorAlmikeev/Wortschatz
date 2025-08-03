import django_filters
from .models import Word, Category

class WordFilter(django_filters.FilterSet):
    part_of_speech_id = django_filters.NumberFilter()
    created_date_time = django_filters.DateFromToRangeFilter()
    definition = django_filters.CharFilter(lookup_expr='icontains')
    categories = django_filters.ModelMultipleChoiceFilter(
        field_name='categories',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Word
        fields = ['part_of_speech_id', 'created_date_time']