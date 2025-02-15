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
import os
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
# MongoDB Cloud Configuration
MONGO_URI = f"mongodb+srv://nshriram1326:{MONGO_PASSWORD}@cluster0.usl45.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client.checkmate


@api_view(['GET'])
def health_check(request):
    return Response({'message': 'API is running'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def register(request):
    freeze_data = db.freeze.find_one(
        {'_id': ObjectId("670dfcc70ad8ed791c734852")}, {'flag': 1, '_id': 0})
    # Default to False if 'flag' is not found
    flag = freeze_data.get('flag', False)
    if flag:
        return Response({'sucess': False, 'message': 'All operations except read are not allowed'}, status=status.HTTP_400_BAD_REQUEST)
    serializer = UserSerializer(data=request.data)

    # Validate the data
    if serializer.is_valid():
        email = request.data.get('email')
        user_collection = db['users']
        existing_user = user_collection.find_one({'email': email})

        if existing_user:
            return Response({'sucess': False, 'message': 'User already exists'}, status=status.HTTP_409_CONFLICT)

        # Create the user using the serializer's create method
        user_data = serializer.create(serializer.validated_data)

        # Manually create JWT tokens
        refresh = RefreshToken()
        access_token = refresh.access_token

        # Attach custom claims to the access token
        access_token['email'] = user_data['email']
        access_token['user_id'] = str(user_data['_id'])

        # Prepare response data with JWT and user ID only
        data = {
            'refresh': str(refresh),
            'access': str(access_token)
        }

        return Response({
            'sucess': True,
            'message': 'User created successfully',
            'data': data
        }, status=status.HTTP_201_CREATED)

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


@api_view(['GET'])
def analytics(request):
    try:
        # Count total users
        total_duplicates = db['duplicate_counter'].find_one(
            {'_id': ObjectId("670d5923251b9fb1f36619d7")})['total']

        total_users = db['users'].count_documents({})

        # Number of users inside campus (mainGate: true)
        inside_campus = db['entryexits'].count_documents({'mainGate': True})

        # Number of users inside concert hall (currentStatus: true)
        inside_concert_hall = db['entryexits'].count_documents(
            {'currentStatus': True})

        # Number of students (role = 0)
        students_count = db['users'].count_documents({'role': 0})

        # Number of VIPs (role = 1)
        vips_count = db['users'].count_documents({'role': 1})

        # Number of faculty (role = 2)
        faculty_count = db['users'].count_documents({'role': 2})

        # Number of students who have paid (paymentStatus: true and role: 0)
        paid_students_count = db['users'].count_documents(
            {'role': 0, 'paymentStatus': True})

        # Students inside concert hall (role = 0 and currentStatus: true)
        students_inside_concert_hall = db['entryexits'].count_documents(
            {'currentStatus': True, 'userId': {'$in': [user['_id'] for user in db['users'].find({'role': 0})]}})

        # VIPs inside concert hall (role = 1 and currentStatus: true)
        # Count documents with currentStatus True for specific userIds
        vips_inside_concert_hall = db['entryexits'].count_documents(
            {'currentStatus': True, 'userId': {'$in': [user['_id'] for user in db['users'].find({'role': 1})]}})

        # Perform aggregation to get the total entered
        aggregate_result = db['dynamicqrs'].aggregate(
            [{"$group": {"_id": None, "totalEntered": {"$sum": "$ppl"}}}])

        # Extract the totalEntered from the aggregate result
        total_entered = next(aggregate_result, {}).get("totalEntered", 0)

        # Add to the total count
        vips_inside_concert_hall += total_entered

        # Faculty inside concert hall (role = 2 and currentStatus: true)
        faculty_inside_concert_hall = db['entryexits'].count_documents(
            {'currentStatus': True, 'userId': {'$in': [user['_id'] for user in db['users'].find({'role': 2})]}})

        # Prepare analytics data
        analytics_data = {
            'total_duplicates': total_duplicates,
            'total_users': total_users,
            'inside_campus': inside_campus,
            'inside_concert_hall': inside_concert_hall,
            'students_count': students_count,
            'vips_count': vips_count,
            'faculty_count': faculty_count,
            'paid_students_count': paid_students_count,
            'students_inside_concert_hall': students_inside_concert_hall,
            'vips_inside_concert_hall': vips_inside_concert_hall,
            'faculty_inside_concert_hall': faculty_inside_concert_hall

        }

        return Response({
            'success': True,
            'message': 'Analytics data fetched successfully',
            'data': analytics_data
        }, status=200)

    except Exception as e:
        return Response({'success': False, 'message': str(e)}, status=500)


# Function to check if the current timestamp falls on the same day
def is_same_day(timestamp1, timestamp2):
    return timestamp1.date() == timestamp2.date()


@api_view(['POST'])
def validate_qr(request):
    try:
        # ObjectId of the duplicate_counter document
        duplicate_counter_id = ObjectId("670d5923251b9fb1f36619d7")
        qr_code = request.data.get('qr_code')
        mode = request.data.get('mode')

        if not qr_code or not mode:
            return Response({'success': False, 'message': 'qr_code and mode are required'}, status=400)

        # Convert the qr_code (string) to ObjectId to match with userId in 'qrdatas'
        try:
            qr_code_obj = ObjectId(qr_code)
        except:
            db['duplicate_counter'].update_one(
                {'_id': duplicate_counter_id}, {'$inc': {'total': 1}})
            return Response({'success': False, 'message': 'Invalid qr_code format'}, status=400)

        # Find the QR data using userId in the 'qrdatas' collection
        qr_collection = db['qrdatas']
        qr_data = qr_collection.find_one({'userId': qr_code_obj})

        if not qr_data:
            return Response({'success': False, 'message': 'QR code not found'}, status=404)

        # Find the user associated with the QR code
        user_collection = db['users']
        user_data = user_collection.find_one({'_id': qr_code_obj})

        if not user_data:
            db['duplicate_counter'].update_one(
                {'_id': duplicate_counter_id}, {'$inc': {'total': 1}})
            return Response({'success': False, 'message': 'User not found'}, status=404)

        # Check if user is VIP
        is_vip = qr_data.get('vip', False)

        # Check entry/exit status from the 'entryexits' collection
        entry_exit_collection = db['entryexits']
        entry_exit_data = entry_exit_collection.find_one(
            {'userId': qr_code_obj})

        if not entry_exit_data:
            return Response({'success': False, 'message': 'Entry/Exit data not found'}, status=404)

        current_status = entry_exit_data.get('currentStatus')
        current_frequency = entry_exit_data.get('frequencyEntry', 0)

        # Handle "entry" mode
        if mode == 'entry':
            # Check if the user is non-VIP and has reached the entry limit
            if not is_vip:
                if current_frequency > 3:
                    return Response({'success': False, 'message': 'Entry limit reached for today'}, status=403)

            if current_status:
                db['duplicate_counter'].update_one(
                    {'_id': duplicate_counter_id}, {'$inc': {'total': 1}})
                return Response({'success': False, 'message': 'Duplicate entry detected'}, status=400)
            else:
                # Increment frequency and mark as entry
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
                db['duplicate_counter'].update_one(
                    {'_id': duplicate_counter_id}, {'$inc': {'total': 1}})
                return Response({'success': False, 'message': 'Duplicate exit detected'}, status=400)
            else:
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
        print(f"Exception: {str(e)}")
        return Response({'success': False, 'message': str(e)}, status=500)


@api_view(['POST'])
def validate_dynamic_qr(request):
    try:
        duplicate_counter_id = ObjectId("670d5923251b9fb1f36619d7")
        qr_code = request.data.get('qr_code')
        mode = request.data.get('mode')
        number = int(request.data.get('number', 0))

        if not qr_code or not mode or number <= 0:
            return Response({'success': False, 'message': 'qr_code, mode, and valid number are required'}, status=400)

        # Fetch the dynamic QR data
        dynamic_qr_collection = db['dynamicqrs']
        dynamic_qr_data = dynamic_qr_collection.find_one(
            {'_id': ObjectId(qr_code)})

        if not dynamic_qr_data:
            return Response({'success': False, 'message': 'Dynamic QR code not found'}, status=404)

        total_ppl = dynamic_qr_data.get('numberofppl', 0)
        entered_ppl = dynamic_qr_data.get('ppl', 0)

        if mode == 'entry':
            if entered_ppl + number > total_ppl:
                # Duplicate entry case
                db['duplicate_counter'].update_one(
                    {'_id': duplicate_counter_id}, {'$inc': {'total': 1}})
                return Response({'success': False, 'message': 'Duplicate entry detected'}, status=400)
            else:
                # Update the entered people count
                dynamic_qr_collection.update_one(
                    {'_id': ObjectId(qr_code)},
                    {'$inc': {'ppl': number}, '$set': {
                        'updatedAt': datetime.now()}}
                )
                data = {'entered_ppl': number, "vip": True}
                return Response({'success': True, 'message': 'Entry approved', "data": data}, status=200)

        elif mode == 'exit':
            if entered_ppl - number < 0:
                # Duplicate exit case
                db['duplicate_counter'].update_one(
                    {'_id': duplicate_counter_id}, {'$inc': {'total': 1}})
                return Response({'success': False, 'message': 'Duplicate exit detected'}, status=400)
            else:
                # Update the entered people count
                dynamic_qr_collection.update_one(
                    {'_id': ObjectId(qr_code)},
                    {'$inc': {'ppl': -number}, '$set': {'updatedAt': datetime.now()}}
                )
                data = {'exited ppl': number, "vip": True}
                return Response({'success': True, 'message': 'Exit approved', "data": data}, status=200)
        else:
            return Response({'success': False, 'message': 'Invalid mode'}, status=400)

    except Exception as e:
        return Response({'success': False, 'message': str(e)}, status=500)


@api_view(['POST'])
def freeze_operations(request):
    try:
        # Access the 'freeze' collection
        freeze_collection = db['freeze']

        # Fetch the freeze document using the Object ID
        freeze_data = freeze_collection.find_one(
            {'_id': ObjectId("670dfcc70ad8ed791c734852")})

        if not freeze_data:
            return Response({'success': False, 'message': 'Freeze data not found'}, status=404)

        # Get the flag value from the request body
        f = request.data.get('flag')

        # Check if the flag is either True or False
        if f is not None and isinstance(f, bool):
            # Update the flag value in the database
            freeze_collection.update_one(
                {'_id': ObjectId("670dfcc70ad8ed791c734852")},
                {'$set': {'flag': f}}
            )
            return Response({'success': True, 'message': 'Flag updated successfully', 'flag': f}, status=200)
        else:
            return Response({'success': False, 'message': 'Invalid flag value'}, status=400)

    except Exception as e:
        return Response({'success': False, 'message': str(e)}, status=500)


@api_view(['GET'])
def get_flag(request):
    try:
        # Access the 'freeze' collection
        freeze_collection = db['freeze']

        # Fetch the freeze document using the Object ID
        freeze_data = freeze_collection.find_one(
            {'_id': ObjectId("670dfcc70ad8ed791c734852")})

        if not freeze_data:
            return Response({'success': False, 'message': 'Freeze data not found'}, status=404)

        # Get the flag value from the request body
        flag = freeze_data.get('flag')
        return Response({'success': True, 'message': 'Flag fetched successfully', 'flag': flag}, status=200)

    except Exception as e:
        return Response({'success': False, 'message': str(e)}, status=500)


@api_view(['GET'])
def get_profile(request):
    user_id = request.data.get('user_id')
    print(user_id)
    user_id = ObjectId(user_id)
    # Retrieve the user document from the 'users' collection
    user_collection = db['users']
    user_data = user_collection.find_one({'_id': user_id})

    if not user_data:
        return Response({'success': False, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    user_data['_id'] = str(user_data['_id'])
    return Response({'success': True, 'message': 'User found', 'data': user_data}, status=status.HTTP_200_OK)
