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
import random
from datetime import datetime
# MongoDB Configuration
MONGO_URI = "mongodb+srv://nshriram1326:vxdQ7yYDz74A9TMR@cluster0.usl45.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client.checkmate


@api_view(['GET'])
def health_check(request):
    return Response({'message': 'API is running'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        email = request.data.get('email')
        user_collection = db['users']
        existing_user = user_collection.find_one({'email': email})

        if existing_user:
            return Response({'sucess': False, 'message': 'User already exists'}, status=status.HTTP_409_CONFLICT)

        user_data = serializer.create(serializer.validated_data)
        data = {'_id': str(user_data['_id'])}
        return Response({'sucess': True, 'message': 'User created successfully', 'data': data}, status=status.HTTP_201_CREATED)

    return Response({'sucess': False, 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

# Login API


@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    firebaseUID = request.data.get('firebaseUID')

    if not email or not firebaseUID:
        return Response({'sucess': False, 'message': 'Email and Firebase UID are required'}, status=status.HTTP_400_BAD_REQUEST)

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
        data = {'refresh': str(refresh), 'access': str(access_token)}
        return Response({
            'sucess': True,
            'message': 'Login successful',
            'data': data
        }, status=status.HTTP_200_OK)

    return Response({'sucess': False, 'message': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


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
            return Response({'sucess': False, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

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
                logging.warning(f"User {user_id} paymentStatus update failed.")

            return Response({'sucess': True, 'message': 'Payment successfully processed'}, status=status.HTTP_200_OK)

        return Response({'sucess': False, 'message': 'Invalid payment status'}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logging.error(f"Error processing payment: {str(e)}")
        return Response({'error': 'An error occurred while processing payment'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_jwt(request):
    user = request.user
    # This should be a CustomUser instance
    data = {'user_id': user._id, 'email': user.email, }
    return Response({
        'sucess': True,
        'message': 'JWT is valid',
        'data': data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    user_id = request.user._id
    user_collection = db['users']
    data = user_collection.find_one({'_id': ObjectId(user_id)})

    if not data:
        return Response({'success': False, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    user_serializer = UserSerializer(data)
    return Response({'success': True, 'message': 'Data Found', 'data': user_serializer.data}, status=status.HTTP_200_OK)


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
            return Response({'success': False, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if required fields are filled
        profile = user_data.get('profileDetails', {})
        required_fields = ['email', 'profileDetails.name',
                           'profileDetails.phoneNumber', 'profileDetails.imageURL', 'profileDetails.college', 'profileDetails.collegeID', 'profileDetails.collegeIdUrl']
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
        if not profile.get('college'):
            missing_fields.append('profileDetails.college')
        if not profile.get('collegeID'):
            missing_fields.append('profileDetails.collegeID')
        if not profile.get('collegeIdUrl'):
            missing_fields.append('profileDetails.collegeIdUrl')

        # Check if profile is complete
        if missing_fields:
            return Response({'success': False, 'message': 'Following Fields are missing', 'data': missing_fields}, status=status.HTTP_200_OK)

        # If all fields are filled
        return Response({'success': True, 'message': 'Profile Complete'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'success': False, 'Message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def validate_qr(request):
    try:
        qr_code = request.data.get('qr_code')
        mode = request.data.get('mode')

        if not qr_code or not mode:
            return Response({'success': False, 'message': 'qr_code and mode are required'}, status=400)

        # Find the QR code in the 'qrdatas' collection
        qr_collection = db['qrdatas']
        qr_data = qr_collection.find_one({'code': qr_code})

        if not qr_data:
            return Response({'success': False, 'message': 'QR code not found'}, status=404)

        # Find the user associated with the QR code
        user_collection = db['users']
        user_data = user_collection.find_one(
            {'_id': ObjectId(qr_data['userId'])})

        if not user_data:
            return Response({'success': False, 'message': 'User not found'}, status=404)

        # Check if user is VIP
        is_vip = qr_data.get('vip', False)

        # Check entry/exit status from the 'entryexit' collection
        entry_exit_collection = db['entryexits']
        entry_exit_data = entry_exit_collection.find_one(
            {'userId': qr_data['userId']})

        if not entry_exit_data:
            return Response({'success': False, 'message': 'Entry/Exit data not found'}, status=404)

        current_status = entry_exit_data.get('currentStatus')

        # Handle "entry" mode
        if mode == 'entry':
            if current_status:
                # If already inside, flag as duplicate entry
                return Response({'success': False, 'message': 'Duplicate entry detected'}, status=200)
            else:
                # Update to mark entry
                entry_exit_collection.update_one(
                    {'_id': entry_exit_data['_id']},
                    {'$set': {'currentStatus': True, 'updatedAt': datetime.now()},
                     '$inc': {'frequencyEntry': 1}}
                )
                return Response({
                    'success': True,
                    'message': 'Entry approved',
                    'data': {'name': user_data['profileDetails']['name'], 'vip': is_vip}
                }, status=200)

        # Handle "exit" mode
        elif mode == 'exit':
            if not current_status:
                # If already outside, flag as duplicate exit
                return Response({'success': False, 'message': 'Duplicate exit detected'}, status=200)
            else:
                # Update to mark exit
                entry_exit_collection.update_one(
                    {'_id': entry_exit_data['_id']},
                    {'$set': {'currentStatus': False, 'updatedAt': datetime.now()},
                     '$inc': {'frequencyExit': 1}}
                )
                return Response({
                    'success': True,
                    'message': 'Exit approved',
                    'data': {'name': user_data['profileDetails']['name'], 'vip': is_vip}
                }, status=200)

        else:
            return Response({'success': False, 'message': 'Invalid mode'}, status=400)

    except Exception as e:
        return Response({'success': False, 'message': str(e)}, status=500)
