from bson import ObjectId  # To handle MongoDB ObjectIds
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .serializers import UserSerializer, PaymentSerializer
from pymongo import MongoClient
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
import logging
# MongoDB Configuration
MONGO_URI = "mongodb+srv://nshriram1326:vxdQ7yYDz74A9TMR@cluster0.usl45.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client.checkmate

# Signup API


@api_view(['POST'])
def register(request):
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


# Configure logging
logging.basicConfig(level=logging.INFO)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def payments(request):
    try:
        # Extract the user_id from the JWT token claims (request.user._id is likely a string or ObjectId directly)
        user_id = request.user._id  # Access _id as an attribute, not as a dictionary key

        # Convert user_id to ObjectId if it's still in string form
        if not isinstance(user_id, ObjectId):
            user_id = ObjectId(user_id)

        # Retrieve the user document from the database based on the ObjectId
        user_collection = db['users']
        user = user_collection.find_one({'_id': user_id})

        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Prepare payment data
        data = request.data.copy()
        # Ensure the userId is set as a string
        data['userId'] = str(user['_id'])

        # Validate payment data
        serializer = PaymentSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        payment_data = serializer.validated_data
        payment_status = payment_data.get('status')

        if payment_status == 'Completed':
            payment_data['createdAt'] = datetime.now()
            payment_data['updatedAt'] = datetime.now()

            # Insert payment record into the 'payments' collection
            db.payments.insert_one(payment_data)

            # Update the user's paymentStatus in the 'users' collection
            update_result = user_collection.update_one(
                {'_id': user_id},  # Use ObjectId directly for querying
                {'$set': {'paymentStatus': True}}  # Set paymentStatus to True
            )

            # Log the result of the update operation
            if update_result.modified_count > 0:
                logging.info(
                    f"User {user_id} paymentStatus updated successfully.")
            else:
                logging.warning(f"User {user_id} paymentStatus update failed. Matched: {
                                update_result.matched_count}, Modified: {update_result.modified_count}")

            return Response({'message': 'Payment successfully processed'}, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid payment status'}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logging.error(f"Error processing payment: {str(e)}")
        return Response({'error': 'An error occurred while processing payment'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_jwt(request):
    user = request.user  # This should be a CustomUser instance
    return Response({
        'user_id': user._id,  # Access the user ID attribute directly
        'email': user.email,
        'name': user.profile_details['name'],  # Access nested profile details
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    user_id = request.user._id
    user_collection = db['users']
    data = user_collection.find_one({'_id': ObjectId(user_id)})

    if not data:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    user_serializer = UserSerializer(data)
    return Response(user_serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_checker(request):
    try:
        # Extract the user's MongoDB _id from the JWT token claims
        user_id = request.user._id

        # Ensure the user_id is an ObjectId for querying MongoDB
        if not isinstance(user_id, ObjectId):
            user_id = ObjectId(user_id)

        # Retrieve the user document from the 'users' collection
        user_collection = db['users']
        user_data = user_collection.find_one({'_id': user_id})

        if not user_data:
            return Response({'success': False, 'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if required fields are filled
        profile = user_data.get('profileDetails', {})
        required_fields = ['email', 'profileDetails.name',
                           'profileDetails.phoneNumber', 'profileDetails.imageURL']
        missing_fields = []

        # Check if these fields are present and not empty
        if not user_data.get('email'):
            missing_fields.append('email')
        if not profile.get('name'):
            missing_fields.append('profileDetails.name')
        if not profile.get('phoneNumber'):
            missing_fields.append('profileDetails.phoneNumber')
        if not profile.get('imageURL'):
            missing_fields.append('profileDetails.imageURL')

        # Check if profile is complete
        if missing_fields:
            return Response({'success': False, 'missing_fields': missing_fields}, status=status.HTTP_200_OK)

        # If all fields are filled
        return Response({'success': True}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
