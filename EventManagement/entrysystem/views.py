from bson import ObjectId  # To handle MongoDB ObjectIds
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .serializers import UserSerializer, PaymentSerializer
from pymongo import MongoClient
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from datetime import datetime
from rest_framework.permissions import IsAuthenticated

# MongoDB Configuration
MONGO_URI = "mongodb+srv://nshriram1326:vxdQ7yYDz74A9TMR@cluster0.usl45.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client.checkmate

# Signup API


@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        email = request.data.get('email')
        user_collection = db['users']
        existing_user = user_collection.find_one({'email': email})

        if existing_user:
            return Response({'error': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user_data = serializer.create(serializer.validated_data)
        return Response({'message': 'User created successfully', '_id': str(user_data['_id'])}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Login API


@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    firebaseUID = request.data.get('firebaseUID')

    if not email or not firebaseUID:
        return Response({'error': 'Email and Firebase UID are required'}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch user data from MongoDB using UserSerializer
    user_data = UserSerializer.get_user_by_email(email)

    if user_data and user_data.get('firebaseUID') == firebaseUID:
        # Create JWT tokens
        refresh = RefreshToken()
        access_token = refresh.access_token

        # Attach custom claims
        access_token['email'] = user_data['email']
        access_token['name'] = user_data['profileDetails']['name']
        access_token['user_id'] = str(user_data['_id'])

        return Response({
            'refresh': str(refresh),
            'access': str(access_token),
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)

    return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def payments(request):
    user = request.user  # This now contains your MongoDB user document

    if not user:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    # Prepare payment data with user ID
    data = request.data.copy()
    # Access the user ID directly as an attribute
    data['userId'] = str(user._id)

    serializer = PaymentSerializer(data=data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    payment_data = serializer.validated_data
    payment_status = payment_data.get('status')

    if payment_status == 'Completed':
        payment_data['createdAt'] = datetime.now()
        payment_data['updatedAt'] = datetime.now()
        db.payments.insert_one(payment_data)

        return Response({'message': 'Payment successfully processed'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_jwt(request):
    user = request.user  # This should be a CustomUser instance
    return Response({
        'user_id': user._id,  # Access the user ID attribute directly
        'email': user.email,
        'name': user.profile_details['name'],  # Access nested profile details
    })
