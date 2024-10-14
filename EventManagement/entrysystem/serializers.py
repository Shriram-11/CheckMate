from rest_framework import serializers
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
# MongoDB Client Configuration
MONGO_URI = "mongodb+srv://nshriram1326:vxdQ7yYDz74A9TMR@cluster0.usl45.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client.checkmate

# User Serializer


class ProfileDetailsSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, max_length=100)
    college = serializers.CharField(required=False, allow_blank=True)
    phoneNumber = serializers.CharField(required=False, allow_blank=True)
    imageURL = serializers.URLField(required=False, allow_blank=True)
    collegeID = serializers.CharField(required=False, allow_blank=True)
    collegeIdUrl = serializers.URLField(required=False, allow_blank=True)


class UserSerializer(serializers.Serializer):
    _id = serializers.CharField(read_only=True)  # MongoDB's _id as read-only
    email = serializers.EmailField(required=True)
    firebaseUID = serializers.CharField(required=True, max_length=100)
    role = serializers.CharField(required=True)
    profileDetails = ProfileDetailsSerializer(required=True)
    paymentStatus = serializers.BooleanField(default=False)

    def create(self, validated_data):
        profile_details = validated_data.pop('profileDetails')
        user_data = {
            'email': validated_data['email'],
            'firebaseUID': validated_data['firebaseUID'],
            'profileDetails': {
                'name': profile_details['name'],
                'college': profile_details.get('college', ''),
                'phoneNumber': profile_details.get('phoneNumber', ''),
                'imageURL': profile_details.get('imageURL', ''),
                'collegeID': profile_details.get('collegeID', ''),
                'collegeIdUrl': profile_details.get('collegeIdUrl', '')
            },
            'paymentStatus': validated_data['paymentStatus'],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        user_collection = db['users']
        inserted_user = user_collection.insert_one(user_data)
        return {**validated_data, '_id': str(inserted_user.inserted_id)}

    def validate_email(self, value):
        user_collection = db['users']
        existing_user = user_collection.find_one({'email': value})
        if existing_user:
            raise serializers.ValidationError(
                "User with this email already exists.")
        return value

    @staticmethod
    def get_user_by_email(email):
        user_collection = db['users']
        user = user_collection.find_one({'email': email})
        return user

    @staticmethod
    def get_user_by_id(user_id):
        user_collection = db['users']
        user = user_collection.find_one({'_id': ObjectId(user_id)})
        return user


class PaymentSerializer(serializers.Serializer):
    # User ID of the person making the payment
    userId = serializers.CharField(required=True)
    amount = serializers.IntegerField(required=True)  # Payment amount
    paymentMethod = serializers.CharField(required=True)  # Method of payment
    status = serializers.CharField(required=True)  # Payment status
    createdAt = serializers.DateTimeField(
        required=True)  # Payment creation timestamp
    updatedAt = serializers.DateTimeField(
        required=True)  # Payment update timestamp
    __v = serializers.IntegerField(required=False)  # Optional version field
