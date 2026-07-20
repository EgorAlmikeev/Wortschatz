import django_filters
from .models import Collection, Tag, Word


class WordFilter(django_filters.FilterSet):
    part_of_speech_id = django_filters.NumberFilter()
    created_date_time = django_filters.DateFromToRangeFilter()
    definition = django_filters.CharFilter(lookup_expr="icontains")
    collection_id = django_filters.NumberFilter(field_name="collections__id")

    class Meta:
        model = Word
        fields = []

class CollectionFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Collection
        fields = []

class TagFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Tag
        fields = []
