from rest_framework import serializers
import hashlib
from pymongo import MongoClient
from datetime import datetime

# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)
db = client.eventdb  # Replace 'eventdb' with your database name


class UserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    # write_only to not expose passwords
    password = serializers.CharField(required=True, write_only=True)
    contact = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    college_name = serializers.CharField(required=True)

    def create(self, validated_data):
        # Hash the password using SHA256
        hashed_password = hashlib.sha256(
            validated_data['password'].encode()).hexdigest()

        # Generate a unique ticket_id using user information
        unique_string = f"{validated_data['name']}{validated_data['email']}{
            validated_data['contact']}{validated_data['college_name']}{datetime.utcnow()}"
        ticket_id = hashlib.sha256(unique_string.encode()).hexdigest()

        # Create a user document
        user_document = {
            "email": validated_data['email'],
            "password": hashed_password,
            "contact": validated_data['contact'],
            "name": validated_data['name'],
            "college_name": validated_data['college_name'],
            "timestamp": datetime.utcnow(),  # Store the current timestamp
            "ticket_id": ticket_id  # Include the ticket_id
        }

        # Insert user into MongoDB
        db.users.insert_one(user_document)  # 'users' is the collection name

        return user_document  # Return the created user document
