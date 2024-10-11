from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import UserSerializer
import hashlib
from pymongo import MongoClient
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime
# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)
db = client.eventdb  # Replace 'eventdb' with your database name

# Create a new user


@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        # This will call the create method in the serializer
        user_document = serializer.save()

        # Convert MongoDB's ObjectId to a string
        user_document['_id'] = str(user_document['_id'])

        return Response({"message": "User created successfully.", "user": user_document}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Login view
@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    # Hash the password using SHA256 for comparison
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # Check if the user exists in the database
    user = db.users.find_one({"email": email, "password": hashed_password})

    if user:
        # Manually create the tokens
        refresh = RefreshToken()
        access = refresh.access_token

        # Attach custom claims (if needed)
        access['email'] = email
        access['ticket_id'] = user["ticket_id"]
        access['exp'] = datetime.utcnow()  # You can customize this

        return Response({
            "message": "Login successful.",
            "refresh": str(refresh),
            "access": str(access),
            "ticket_id": user["ticket_id"]
        }, status=status.HTTP_200_OK)

    return Response({"message": "Invalid email or password."}, status=status.HTTP_400_BAD_REQUEST)
