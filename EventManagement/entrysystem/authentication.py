from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from pymongo import MongoClient
from bson import ObjectId
from .serializers import UserSerializer  # Import the UserSerializer

# MongoDB Configuration
MONGO_URI = "mongodb+srv://nshriram1326:vxdQ7yYDz74A9TMR@cluster0.usl45.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)  # Use settings for MongoDB URI
db = client.checkmate  # Your database name

# Custom user class to mimic Django User behavior


class CustomUser:
    def __init__(self, user_data):
        self._id = str(user_data['_id'])  # Convert ObjectId to string
        self.email = user_data['email']
        self.profile_details = user_data['profileDetails']
        self.is_authenticated = True  # Set to True to mimic authentication


class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user_id = validated_token.get('user_id')
        if not user_id:
            raise AuthenticationFailed('User ID not found in token')

        # Attempt to convert user_id to ObjectId
        try:
            user_id = ObjectId(user_id)
        except Exception:
            raise AuthenticationFailed('Invalid user ID format')

        # Use UserSerializer to find the user by ID
        user_data = UserSerializer.get_user_by_id(user_id)
        if user_data is None:
            raise AuthenticationFailed('User not found')

        return CustomUser(user_data)  # Return a CustomUser instance

    def authenticate(self, request):
        # Call the superclass method to extract the user
        auth_result = super().authenticate(request)
        if auth_result is None:
            return None  # Properly handle None return

        user, _ = auth_result  # Unpack only if auth_result is not None
        return user, None
