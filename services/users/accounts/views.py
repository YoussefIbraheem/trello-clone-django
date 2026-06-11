import logging

from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, response, status, views
from rest_framework_simplejwt import tokens
from .models import User, UserProfile
from .serializers import (
    UserLoginSerializer,
    UserLogoutSerializer,
    UserPasswordChangeSerializer,
    UserProfileSerializer,
    UserRegisterationSerializer,
    UserSerializer,
)

logger = logging.getLogger(__name__)

class ActorMixin:
    def get_actor_id(self):
        request = getattr(self, "request", None)

        if request and getattr(request, "user", None):
            user = request.user
            if user.is_authenticated:
                return user.id

        return None


# Create your views here.


class UserRegisterationView(ActorMixin,views.APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @swagger_auto_schema(request_body=UserRegisterationSerializer)
    def post(self, request):
        serializer = UserRegisterationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            actor_id = self.get_actor_id() or user.id
            user._actor_id = actor_id

            refresh = tokens.RefreshToken.for_user(user=user)

            return response.Response(
                {
                    "message": "User registered successfully",
                    "user": UserSerializer(user).data,
                    "tokens": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(ActorMixin,views.APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @swagger_auto_schema(request_body=UserLoginSerializer)
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data

            actor_id = self.get_actor_id() or user.id
            user._actor_id = actor_id

            refresh = tokens.RefreshToken.for_user(user=user)

            logger.warning(
                f"REFRESH TOKEN FOR USER {user.username}: {str(refresh)}", exc_info=True
            )

            return response.Response(
                {
                    "message": "User logged in successfully",
                    "user": UserSerializer(user).data,
                    "tokens": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return response.Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )


class UserProfileView(ActorMixin,views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(responses={200: UserProfileSerializer()})
    def get(self, request):
        try:
            profile = request.user.profile
            serializer = UserProfileSerializer(profile).data
            return response.Response(serializer)

        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
            serializer = UserProfileSerializer(profile).data
            return response.Response(serializer)

    @swagger_auto_schema(
        request_body=UserProfileSerializer, responses={200: UserProfileSerializer()}
    )
    def put(self, request):
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            actor_id = self.get_actor_id() or request.user.id
            request.user._actor_id = actor_id

            return response.Response(serializer.data)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserChangePasswordView(ActorMixin,views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=UserPasswordChangeSerializer,
        responses={
            200: "Password Updated Successfully!",
        },
    )
    def post(self, request):
        serializer = UserPasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            user = serializer.save()

            actor_id = self.get_actor_id() or user.id
            user._actor_id = actor_id

            return response.Response(
                {"message": "Password Updated Successfully!"},
                status=status.HTTP_200_OK,
            )
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(ActorMixin,views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=UserLogoutSerializer,
        responses={200: "User logged out successfully."},
    )
    def post(self, request):
        serializer = UserLogoutSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            user = serializer.save()

        # Actor assigning is not needed here
 
            return response.Response(
                {"message": "User logged out successfully."},
                status=status.HTTP_200_OK,
            )
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAdminUser]
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["email", "username", "is_verified"]

    @swagger_auto_schema(serializer_class=UserSerializer(many=True))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class UserDetailsView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAdminUser]
    serializer_class = UserSerializer

    @swagger_auto_schema(serializer_class=UserSerializer)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class UserVerificationEmailView(ActorMixin,views.APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @swagger_auto_schema(
        manual_parameters=[],
        responses={200: "User verified successfully."},
    )
    def post(self, request):

        email = request.data.get("email")
        code = request.data.get("code")

        try:
            user = User.objects.get(email=email)
            verification = user.verification

            if verification.code == code:
                logger.info(
                    f"Verifying user {user.email} ,Given code:{code}, Expected code:{verification.code}"
                )
                user.is_verified = True
                user.save()

                actor_id = self.get_actor_id() or user.id
                user._actor_id = actor_id

                verification.delete()

                return response.Response("User verified successfully.")
            else:
                return response.Response(
                    f"Error With Verification Code :{e}",
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            return response.Response(
                f"Error Verifying User:{e}", status=status.HTTP_400_BAD_REQUEST
            )
