from rest_framework import serializers
from datetime import datetime

from services.models import Service, MedicalSpecialty, Event, Vaccination, AnalysisPackage, AnalysisTest, EventType, \
    TreatmentPlan, TreatmentIntake, BloodDonation, DonationCenter


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


class DonationCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonationCenter
        fields = ("id", "title", "slug", "address", "city", "phone")


class BloodDonationSerializer(serializers.ModelSerializer):
    center = serializers.PrimaryKeyRelatedField(queryset=DonationCenter.objects.all())
    date = serializers.DateField(required=False)
    time = serializers.TimeField(required=False)

    class Meta:
        model = BloodDonation
        fields = ("id", "center", "date", "time")


class EventSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)
    medical_specialty = MedicalSpecialtySerializer(read_only=True)
    vaccination = VaccinationSerializer(read_only=True)
    analysis_test = AnalysisTestSerializer(read_only=True)
    blood_donation = BloodDonationSerializer(read_only=True)

    service_id = serializers.PrimaryKeyRelatedField(
        source="service", queryset=Service.objects.all(),
        write_only=True, required=False, allow_null=True, label="Service id"
    )
    medical_specialty_id = serializers.PrimaryKeyRelatedField(
        source="medical_specialty", queryset=MedicalSpecialty.objects.all(),
        write_only=True, required=False, allow_null=True, label="Medical specialty id"
    )
    vaccination_id = serializers.PrimaryKeyRelatedField(
        source="vaccination", queryset=Vaccination.objects.all(),
        write_only=True, required=False, allow_null=True, label="Vaccination id"
    )
    analysis_test_id = serializers.PrimaryKeyRelatedField(
        source="analysis_test", queryset=AnalysisTest.objects.all(),
        write_only=True, required=False, allow_null=True, label="Analysis test id"
    )

    blood_donation_id = serializers.PrimaryKeyRelatedField(
        source="blood_donation",
        queryset=BloodDonation.objects.all(),
        write_only=True, required=False, allow_null=True,
        label="Blood donation id"
    )
    donation_center_id = serializers.PrimaryKeyRelatedField(
        queryset=DonationCenter.objects.all(),
        write_only=True, required=False, allow_null=True,
        label="Donation center"
    )

    blood_donation_data = BloodDonationSerializer(write_only=True, required=False)

    event_type = serializers.ChoiceField(choices=EventType.choices, read_only=True)

    class Meta:
        model = Event
        fields = (
            "id", "name", "short_description",
            "start_date", "start_time",
            "service", "service_id",
            "medical_specialty", "medical_specialty_id",
            "vaccination", "vaccination_id",
            "analysis_test", "analysis_test_id",
            "blood_donation", "blood_donation_id",
            "donation_center_id", "blood_donation_data",
            "event_type", "created_at",
        )
        read_only_fields = ("id", "name", "event_type", "created_at")

    def validate(self, attrs):
        dc = attrs.pop("donation_center_id", None)
        if dc is not None:
            bd = attrs.setdefault("blood_donation_data", {})
            bd["center"] = dc
            bd.setdefault("date", attrs.get("start_date"))
            bd.setdefault("time", attrs.get("start_time"))

        picked = sum(1 for k in ("medical_specialty", "vaccination", "analysis_test", "service", "blood_donation")
                     if attrs.get(k))
        if attrs.get("blood_donation_data"):
            picked += 1
        if picked > 1:
            raise serializers.ValidationError(
                "Pick only one of: medical_specialty_id, vaccination_id, analysis_test_id, "
                "service_id, blood_donation_id / donation_center / blood_donation_data."
            )
        if picked == 0:
            raise serializers.ValidationError(
                "You must provide one related field (service or specialty/vaccination/analysis_test or blood_donation)."
            )

        bd = attrs.get("blood_donation_data")
        if bd is not None:
            if bd.get("date") is None or bd.get("time") is None:
                raise serializers.ValidationError(
                    "For blood donation provide start_date and start_time "
                    "(or date/time in blood_donation_data)."
                )
        return attrs

    def create(self, validated):
        request = self.context.get("request")
        bd_nested = validated.pop("blood_donation_data", None)

        if bd_nested:
            bd_nested["user"] = request.user
            validated["blood_donation"] = BloodDonation.objects.create(**bd_nested)

        event = super().create(validated)

        if event.blood_donation_id:
            event.event_type = EventType.BLOOD_DONATION
            event.name = event.name or "Blood donation"
        elif event.vaccination_id:
            event.event_type = EventType.VACCINATION
            event.name = event.name or event.vaccination.title
        elif event.analysis_test_id:
            event.event_type = EventType.ANALYSIS_TEST
            event.name = event.name or event.analysis_test.title
        elif event.medical_specialty_id:
            event.event_type = EventType.VISIT
            event.name = event.name or f"Visit to {event.medical_specialty.title}"
        elif event.service_id:
            event.event_type = EventType.OTHER
            event.name = event.name or event.service.title

        event.save(update_fields=["event_type", "name"])
        return event


class EventRetrySerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)
    medical_specialty = MedicalSpecialtySerializer(read_only=True)
    vaccination = VaccinationSerializer(read_only=True)
    analysis_test = AnalysisTestSerializer(read_only=True)

    blood_donation = serializers.IntegerField(source="blood_donation_fk_id", read_only=True)
    donation_center = DonationCenterSerializer(source="blood_donation.center", read_only=True)

    class Meta:
        model = Event
        fields = (
            "id", "name", "start_date", "start_time",
            "medical_specialty", "vaccination", "analysis_test", "service",
            "blood_donation", "donation_center",
            "event_type", "created_at",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {k: v for k, v in data.items() if v not in [None, False, "", [], {}]}
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



