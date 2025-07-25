from rest_framework import serializers

from services.models import Service, MedicalSpecialty, Event, Vaccination, AnalysisPackage, AnalysisTest


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


class MedicalSpecialtySerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalSpecialty
        fields = (
            "id",
            "title",
            "slug",
            "description",
        )


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = (
            "id",
            "name",
            "date",
            "created_at"
        )
        read_only_fields = ("id", "created_at")


class VaccinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vaccination
        fields = (
            "id",
            "title",
            "slug",
            "description",
            "vaccine_info"
        )


class AnalysisTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisTest
        fields = (
            "id",
            "package",
            "title",
            "description",
        )


class AnalysisPackageSerializer(serializers.ModelSerializer):
    test = AnalysisTestSerializer(many=True, read_only=True, source="analysistest_set")

    class Meta:
        model = AnalysisPackage
        fields = (
            "id",
            "title",
            "test"
        )
