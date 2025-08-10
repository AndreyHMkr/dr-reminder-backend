from rest_framework import serializers
from datetime import datetime

from services.models import Service, MedicalSpecialty, Event, Vaccination, AnalysisPackage, AnalysisTest, EventType, \
    TreatmentPlan, TreatmentIntake


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

class EventSerializer(serializers.ModelSerializer):
    # write-only ID
    medical_specialty_id = serializers.PrimaryKeyRelatedField(
        source="medical_specialty",
        queryset=MedicalSpecialty.objects.all(),
        write_only=True, required=False, allow_null=True,
    )
    vaccination_id = serializers.PrimaryKeyRelatedField(
        source="vaccination",
        queryset=Vaccination.objects.all(),
        write_only=True, required=False, allow_null=True,
    )
    analysis_test_id = serializers.PrimaryKeyRelatedField(
        source="analysis_test",
        queryset=AnalysisTest.objects.all(),
        write_only=True, required=False, allow_null=True,
    )

    medical_specialty = MedicalSpecialtySerializer(read_only=True)
    vaccination = VaccinationSerializer(read_only=True)
    analysis_test = AnalysisTestSerializer(read_only=True)

    blood_donation = serializers.BooleanField(required=False)
    event_type = serializers.ChoiceField(choices=EventType.choices, read_only=True)

    class Meta:
        model = Event
        fields = (
            "id", "name", "short_description", "start_date", "start_time",
            "medical_specialty_id", "vaccination_id", "analysis_test_id",
            "medical_specialty", "vaccination", "analysis_test",
            "blood_donation", "event_type", "created_at",
        )
        read_only_fields = ("id", "name", "event_type", "created_at")




class EventRetrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = (
            "id",
            "name",
            "start_date",
            "start_time",
            "medical_specialty",
            "vaccination",
            "analysis_test",
            "blood_donation",
            "event_type",
            "created_at"
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {key: val for key, val in data.items() if val not in [None, False, "", [], {}]}





class TimesCharField(serializers.CharField):
    def to_internal_value(self, data):
        if not data:
            raise serializers.ValidationError("Times cannot be empty.")
        times = [t.strip() for t in data.split(",") if t.strip()]
        parsed_times = []
        for t in times:
            try:
                parsed_times.append(datetime.strptime(t, "%H:%M").time())
            except ValueError:
                raise serializers.ValidationError(f"Invalid time format: {t}. Use HH:MM.")
        return parsed_times


class TreatmentPlanCreateSerializer(serializers.ModelSerializer):
    time_of_taking_medications = TimesCharField(write_only=True,
                                                help_text="Time separated by commas, for example: 08:00, 13:00, 20:00")

    class Meta:
        model = TreatmentPlan
        fields = (
            "id",
            "name_of_medicine",
            "description",
            "start_date",
            "finish_date",
            "time_of_taking_medications",
        )

    def validate(self, attrs):
        if attrs["start_date"] > attrs["finish_date"]:
            raise serializers.ValidationError("Start date must be later than finish date.")
        return attrs

    def create(self, validated_data):
        times = validated_data.pop("time_of_taking_medications")
        user = self.context["request"].user
        plan = TreatmentPlan.objects.create(user=user, **validated_data)

        for t in times:
            intake = TreatmentIntake.objects.create(plan=plan, time=t)
            intake.schedule_next_run()

        return plan


class TreatmentPlanReadSerializer(serializers.ModelSerializer):
    times = serializers.SerializerMethodField()

    class Meta:
        model = TreatmentPlan
        fields = (
            "id",
            "name_of_medicine",
            "description",
            "start_date",
            "finish_date",
            "times"
        )

    def get_times(self, obj):
        return [i.time.strftime("%H:%M") for i in obj.intakes.all()]
