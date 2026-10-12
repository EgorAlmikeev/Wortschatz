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

class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    pass


class CollectionFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    # Comma-separated tag ids, e.g. ?tag_id=1,2 — matches collections tagged
    # with any of the given tags ("category" in the UI).
    tag_id = NumberInFilter(field_name="tags__id", distinct=True)

    class Meta:
        model = Collection
        fields = []

class TagFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Tag
        fields = []
