from rest_framework import serializers
from .models import LostReport, FoundReport, Category, Location


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name']


class LostReportSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    location = LocationSerializer(read_only=True)
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(), source='location', write_only=True, required=False
    )
    reporter = serializers.StringRelatedField(read_only=True)
    matched_with = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = LostReport
        fields = [
            'id', 'reporter', 'category', 'category_id', 'title', 'description',
            'location', 'location_id', 'image', 'serial_number', 'date_reported',
            'status', 'matched_with', 'colour', 'brand', 'model'
        ]
        read_only_fields = ['reporter', 'date_reported', 'matched_with', 'status']

    def create(self, validated_data):
        validated_data['reporter'] = self.context['request'].user
        return super().create(validated_data)


class FoundReportSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    location = LocationSerializer(read_only=True)
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(), source='location', write_only=True, required=False
    )
    dropped_location = LocationSerializer(read_only=True)
    dropped_location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(), source='dropped_location', write_only=True, required=False
    )
    reporter = serializers.StringRelatedField(read_only=True)
    matched_with = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = FoundReport
        fields = [
            'id', 'reporter', 'category', 'category_id', 'title', 'description',
            'location', 'location_id', 'dropped_location', 'dropped_location_id',
            'image', 'serial_number', 'date_reported',
            'status', 'matched_with', 'colour', 'brand', 'model', 'claimed_by', 'picked_up_date'
        ]
        read_only_fields = ['reporter', 'date_reported', 'matched_with', 'status', 'claimed_by', 'picked_up_date']

    def create(self, validated_data):
        validated_data['reporter'] = self.context['request'].user
        return super().create(validated_data)
