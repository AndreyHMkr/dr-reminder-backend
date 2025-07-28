from rest_framework import serializers

from services.models import Service, MedicalSpecialty, Event, Vaccination, AnalysisPackage, AnalysisTest, EventType


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

    medical_specialty = serializers.SlugRelatedField(
        slug_field='title',
        queryset=MedicalSpecialty.objects.all(),
        required=False,
        allow_null=True,
    )
    vaccination = serializers.SlugRelatedField(
        slug_field='title',
        queryset=Vaccination.objects.all(),
        required=False,
        allow_null=True,
    )
    analysis_test = serializers.SlugRelatedField(
        slug_field='title',
        queryset=AnalysisTest.objects.all(),
        required=False,
        allow_null=True,
    )
    blood_donation = serializers.BooleanField(required=False)
    event_type = serializers.ChoiceField(choices=EventType.choices, read_only=True)

    class Meta:
        model = Event
        fields = (
            "id",
            "name",
            "short_description",
            "start_date",
            "start_time",
            "medical_specialty",
            "vaccination",
            "analysis_test",
            "blood_donation",
            "event_type",
            "created_at"
        )
        read_only_fields = ("id", "name", "event_type", "created_at")

    def validate(self, attrs):
        types_selected = [
            bool(attrs.get("medical_specialty")),
            bool(attrs.get("vaccination")),
            bool(attrs.get("analysis_test")),
            bool(attrs.get("blood_donation")),
        ]
        if sum(types_selected) != 1:
            raise serializers.ValidationError(
                "Only one of the fields [specialty, vaccination, test, donation] is allowed."
            )
        return attrs


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
