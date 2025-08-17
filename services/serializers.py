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



class EventSerializer(serializers.ModelSerializer):
    donation_center = serializers.SlugRelatedField(
        slug_field="title",
        queryset=DonationCenter.objects.all(),
        write_only=True, required=False, allow_null=True,
    )
    blood_donation = serializers.IntegerField(source="blood_donation_id", read_only=True)


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

    service_id = serializers.PrimaryKeyRelatedField(
        source="service",
        queryset=Service.objects.all(),
        write_only=True, required=False, allow_null=True,
    )
    medical_specialty = MedicalSpecialtySerializer(read_only=True)
    vaccination = VaccinationSerializer(read_only=True)
    analysis_test = AnalysisTestSerializer(read_only=True)
    service = ServiceSerializer(read_only=True)

    event_type = serializers.ChoiceField(choices=EventType.choices, read_only=True)


    class Meta:
        model = Event
        fields = (
            "id", "name", "short_description", "start_date", "start_time",
            "medical_specialty_id", "vaccination_id", "analysis_test_id",
            "service_id", "service",
            "medical_specialty", "vaccination", "analysis_test", "service",
            "donation_center",
            "blood_donation", "event_type", "created_at",
        )
        read_only_fields = ("id", "name", "event_type", "created_at")

    def validate(self, attrs):
        picked = 0
        if attrs.get("medical_specialty"): picked += 1
        if attrs.get("vaccination"): picked += 1
        if attrs.get("analysis_test"): picked += 1
        if attrs.get("service"): picked += 1
        if attrs.get("donation_center"): picked += 1  # <-- вот так

        if picked > 1:
            raise serializers.ValidationError(
                "Only one: medical_specialty_id, vaccination_id, "
                "analysis_test_id, service_id або donation_center."
            )
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        center = validated_data.pop("donation_center", None)  # <-- объект DonationCenter или None

        if center:
            donation = BloodDonation.objects.create(
                user=user,
                center=center,
                date=validated_data["start_date"],
                time=validated_data["start_time"],
            )
            validated_data["blood_donation"] = donation


        return super().create(validated_data)

    def update(self, instance, validated_data):
        center = validated_data.pop("donation_center", None)

        is_bd = (instance.blood_donation_id is not None) or (center is not None)
        if is_bd:
            donation = getattr(instance, "blood_donation", None)
            if donation is None:
                donation = BloodDonation.objects.create(
                    user=instance.user,
                    center=center,
                    date=validated_data.get("start_date", instance.start_date),
                    time=validated_data.get("start_time", instance.start_time),
                )
                validated_data["blood_donation"] = donation
            else:
                if center is not None:
                    donation.center = center
                if "start_date" in validated_data:
                    donation.date = validated_data["start_date"]
                if "start_time" in validated_data:
                    donation.time = validated_data["start_time"]
                donation.save()

        return super().update(instance, validated_data)


class EventRetrySerializer(serializers.ModelSerializer):
    blood_donation = serializers.IntegerField(source="blood_donation_fk_id", read_only=True)
    donation_center = DonationCenterSerializer(source="blood_donation_fk.center", read_only=True)

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


class BloodDonationSerializer(serializers.ModelSerializer):
    center = serializers.PrimaryKeyRelatedField(queryset=DonationCenter.objects.all())

    class Meta:
        model = BloodDonation
        fields = (
            "id",
            "center",
            "date",
            "time"
        )
