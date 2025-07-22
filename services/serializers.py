from rest_framework import serializers

from services.models import Service, Speciality


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = (
            "id",
            "title",
            "description",
            "icon",
            "order"
        )

class SpecialitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Speciality
        fields = (
            "name",
            "slug",
            "description",
            "order"
        )