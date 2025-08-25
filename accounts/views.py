from rest_framework import generics, status, parsers
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from accounts.models import UserProfile, HealthIndicators, MedicalDocument, UserSettings
from rest_framework import viewsets
from django.contrib.auth import get_user_model
from accounts.serializers import UserSerializer, ResetPasswordSerializer, ResetPasswordConfirmSerializer, \
    UserProfileSerializer, HealthIndicatorsSerializer, MedicalDocumentSerializer, MedicalDocumentBulkUploadSerializer, \
    DeleteAccountSerializer, ChangePasswordSerializer, UserSettingsSerializer
from services.models import BloodDonation, DonationCenter, Event
from services.serializers import BloodDonationSerializer, DonationCenterSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.CreateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    queryset = UserProfile.objects.all()


class UserPhotoView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            return Response({"detail": "User profile does not exist."}, status=404)

        if profile.image_profile:
            profile.image_profile.delete(save=False)
            profile.image_profile = None
            profile.save(update_fields=["image_profile"])

        return Response(status=status.HTTP_204_NO_CONTENT)


class MedicalDocumentViewSet(viewsets.ModelViewSet):
    serializer_class = MedicalDocumentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return MedicalDocument.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["post"], url_path="bulk")
    def bulk_upload(self, request, *args, **kwargs):
        ser = MedicalDocumentBulkUploadSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        docs = ser.save()
        return Response(MedicalDocumentSerializer(docs, many=True).data, status=status.HTTP_201_CREATED)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        try:
            return user.userprofile
        except UserProfile.DoesNotExist:
            raise NotFound("User profile does not exist.")


class ResetPasswordView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordSerializer
    parser_classes = [parsers.JSONParser, parsers.FormParser, parsers.MultiPartParser]

    def post(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save(request=request)
        from rest_framework.response import Response
        from rest_framework import status
        return Response({"detail": "Password reset email sent."}, status=status.HTTP_200_OK)

class ResetPasswordConfirmView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordConfirmSerializer
    parser_classes = [parsers.JSONParser, parsers.FormParser, parsers.MultiPartParser]

    def post(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save()
        from rest_framework.response import Response
        from rest_framework import status
        return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
class HealthIndicatorsView(viewsets.ModelViewSet):
    serializer_class = HealthIndicatorsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return HealthIndicators.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        instance, _ = HealthIndicators.objects.update_or_create(
            user=self.request.user,
            defaults=serializer.validated_data
        )
        serializer.instance = instance


class DonationCenterViewSet(ModelViewSet):
    queryset = DonationCenter.objects.all().order_by("city", "title")
    serializer_class = DonationCenterSerializer
    permission_classes = [IsAuthenticated]


class BloodDonationView(viewsets.ModelViewSet):
    serializer_class = BloodDonationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BloodDonation.objects.filter(user=self.request.user).select_related("center")

    def perform_create(self, serializer):
        donation = serializer.save(user=self.request.user)
        Event.objects.update_or_create(
            blood_donation=donation,
            defaults={
                "user": donation.user,
                "start_date": donation.date,
                "start_time": donation.time,
            },
        )

    def perform_update(self, serializer):
        donation = serializer.save()
        Event.objects.update_or_create(
            blood_donation=donation,
            defaults={
                "user": donation.user,
                "start_date": donation.date,
                "start_time": donation.time,
            },
        )

    def perform_destroy(self, instance):
        Event.objects.filter(blood_donation=instance).delete()
        super().perform_destroy(instance)


class MeSettingsView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSettingsSerializer

    def get_object(self):
        return UserSettings.objects.get_or_create(user=self.request.user)[0]


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = ChangePasswordSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response({"detail": "Password updated."}, status=status.HTTP_200_OK)


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = DeleteAccountSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)

        request.user.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)




class ChangeLoginView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        User = get_user_model()
        new_email = request.data.get("email")
        if not new_email:
            return Response({"detail": "New email is required"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=new_email).exists():
            return Response({"detail": "This email is already taken."}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        user.email = new_email
        user.save(update_fields=["email"])
        return Response({"detail": "Login (email) updated successfully"}, status=status.HTTP_200_OK)