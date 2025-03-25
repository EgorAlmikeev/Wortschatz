from rest_framework import serializers
from .models import Word, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class WordSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source = 'owner.username')
    categories = serializers.PrimaryKeyRelatedField(many=True, queryset=Category.objects.all())
    genus_name = serializers.CharField(source = 'get_genus_display', read_only = True)

    class Meta:
        model = Word
        fields = ['id', 'created_date_time', 'definition', 'translation', 'example', 'genus_id', 'genus_name', 'categories', 'usage_count']