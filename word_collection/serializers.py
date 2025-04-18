from rest_framework import serializers

from .models import Word, Category

class CategorySerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Category
        fields = ['owner', 'id', 'name']

class WordSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    categories = serializers.PrimaryKeyRelatedField(many=True, queryset=Category.objects.all())
    genus_name = serializers.CharField(source='get_genus_id_display', read_only=True)
    part_of_speech_name = serializers.CharField(source='get_part_of_speech_id_display', read_only=True)

    class Meta:
        model = Word
        fields = ['owner', 
                  'id', 
                  'created_date_time', 
                  'definition', 
                  'translations', 
                  'examples', 
                  'other_forms', 
                  'usage_variants', 
                  'part_of_speech_id', 
                  'part_of_speech_name', 
                  'genus_id', 
                  'genus_name',
                  'categories', 
                  'usage_count'
                  ]