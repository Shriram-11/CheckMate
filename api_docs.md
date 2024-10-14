### **EventManagement Project API Documentation**

---

### 1. **Health Check API**

- **Endpoint**: `/api/entrysystem/health_check/`
- **Method**: `GET`
- **Permission**: None
- **Description**: Verifies if the API service is running.
- **Response**:
  - **Success**:
    ```json
    {
      "message": "API is running"
    }
    ```

### 2. **User Registration API**

- **Endpoint**: `/api/entrysystem/register/`
- **Method**: `POST`
- **Description**: Allows a new user to register by providing email and Firebase UID.
- **Request Body**:
  ```json
  {
    "email": "student@example.com",
    "firebaseUID": "uniqueFirebaseUID123",
    "profileDetails": {
      "name": "John Doe",
      "college": "ABC University",
      "phoneNumber": "1234567890",
      "imageURL": "http://example.com/image.jpg",
      "collegeID": "COL12345",
      "collegeIdUrl": "http://example.com/college-id.jpg"
    },
    "paymentStatus": true
  }
  ```
- **Response**:
  - **Success**:
    ```json
    {
      "message": "User created successfully",
      "_id": "USER_MONGO_ID"
    }
    ```
  - **Error**:
    ```json
    {
      "error": "User already exists"
    }
    ```
  - **Validation Error**:
    ```json
    {
      "email": ["This field is required."]
    }
    ```

---

### 2. **User Login API**

- **Endpoint**: `/api/entrysystem/login/`
- **Method**: `POST`
- **Description**: Authenticates the user by verifying email and Firebase UID, and returns JWT tokens.
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "firebaseUID": "UID1234567890"
  }
  ```
- **Response**:
  - **Success**:
    ```json
    {
      "refresh": "REFRESH_TOKEN",
      "access": "ACCESS_TOKEN",
      "message": "Login successful"
    }
    ```
  - **Error**:
    ```json
    {
      "error": "Invalid credentials"
    }
    ```
  - **Validation Error**:
    ```json
    {
      "error": "Email and Firebase UID are required"
    }
    ```

---

### 3. **Payment Processing API**

- **Endpoint**: `/api/entrysystem/payments/`
- **Method**: `POST`
- **Permission**: `IsAuthenticated`
- **Description**: Handles payment processing and updates the user's payment status.
- **Request Body**:
  ```json
  {
    "status": "Completed",
    "amount": 100
  }
  ```
- **Response**:
  - **Success**:
    ```json
    {
      "message": "Payment successfully processed"
    }
    ```
  - **Error**:
    ```json
    {
      "error": "User not found"
    }
    ```
  - **Payment Status Error**:
    ```json
    {
      "error": "Invalid payment status"
    }
    ```

---

### 4. **Check JWT Token API**

- **Endpoint**: `/api/entrysystem/check_jwt/`
- **Method**: `GET`
- **Permission**: `IsAuthenticated`
- **Description**: Returns the user details based on the authenticated JWT token.
- **Response**:
  ```json
  {
    "user_id": "USER_MONGO_ID",
    "email": "user@example.com",
    "name": "User Name"
  }
  ```

---

### 5. **User Profile API**

- **Endpoint**: `/api/entrysystem/profile/`
- **Method**: `GET`
- **Permission**: `IsAuthenticated`
- **Description**: Fetches the full profile details of the logged-in user.
- **Response**:
  ```json
  {
    "_id": "USER_MONGO_ID",
    "email": "user@example.com",
    "firebaseUID": "UID1234567890",
    "profileDetails": {
      "name": "User Name",
      "college": "Some College",
      "phoneNumber": "+91 9876543210",
      "imageURL": "https://example.com/profile.jpg"
    },
    "paymentStatus": true,
    "created_at": "2024-10-12T14:53:03.917Z",
    "updated_at": "2024-10-12T14:53:03.917Z"
  }
  ```
- **Error**:
  ```json
  {
    "error": "User not found"
  }
  ```

---

### 6. **Profile Completeness Check API**

- **Endpoint**: `/api/entrysystem/profile_checker/`
- **Method**: `GET`
- **Permission**: `IsAuthenticated`
- **Description**: Checks whether the user's profile is complete by verifying essential fields (email, name, phone number, and image URL).
- **Response**:
  - **Complete Profile**:
    ```json
    {
      "success": true
    }
    ```
  - **Incomplete Profile**:
    ```json
    {
      "success": false,
      "missing_fields": [
        "profileDetails.phoneNumber",
        "profileDetails.imageURL"
      ]
    }
    ```
  - **Error**:
    ```json
    {
      "success": false,
      "error": "User not found"
    }
    ```

### 7. **Profile Completeness Check API**

- **Endpoint**: `/api/entrysystem/health_check/`
- **Method**: `GET`
- **Permission**: None
- **Description**: Checks the health of the API.
- **Response**:
  - **Complete Profile**:
    ```json
    {
      "message": "API is running"
    }
    ```

### 8. **QR Validation API**

- **Endpoint**: `/api/entrysystem/validate_qr/`
- **Method**: `POST`
- **Description**: Validates a QR code for entry or exit, and checks the current entry status of the user associated with the QR code.

- **Request Body**:

  ```json
  {
    "qr_code": "670a1b65847c0d3f9c57b70c",
    "mode": "entry" // or "exit"
  }
  ```

- **Response Examples**:

1. **Successful Entry Approval**:

   ```json
   {
     "success": true,
     "message": "Entry approved",
     "data": {
       "name": "Ankita Sharma",
       "vip": true
     }
   }
   ```

2. **Successful Exit Approval**:

   ```json
   {
     "success": true,
     "message": "Exit approved",
     "data": {
       "name": "Ankita Sharma",
       "vip": true
     }
   }
   ```

3. **Duplicate Entry** (if user is already inside):

   ```json
   {
     "success": false,
     "message": "Duplicate entry detected"
   }
   ```

4. **Duplicate Exit** (if user is already outside):

   ```json
   {
     "success": false,
     "message": "Duplicate exit detected"
   }
   ```

5. **Invalid QR Code**:

   ```json
   {
     "success": false,
     "message": "QR code not found"
   }
   ```

6. **Invalid Mode**:

   ```json
   {
     "success": false,
     "message": "Invalid mode"
   }
   ```

7. **Missing `qr_code` or `mode` in Request**:

   ```json
   {
     "success": false,
     "message": "qr_code and mode are required"
   }
   ```

8. **User Not Found**:

   ```json
   {
     "success": false,
     "message": "User not found"
   }
   ```

9. **Entry/Exit Data Not Found**:

   ```json
   {
     "success": false,
     "message": "Entry/Exit data not found"
   }
   ```

10. **Internal Server Error**:
    ```json
    {
      "success": false,
      "message": "An error occurred while processing the request"
    }
    ```

### 9. **Entry System Analytics API**

- **Endpoint**: `/api/entrysystem/analytics/`
- **Method**: `GET`
- **Permission**: Admin
- **Description**: Provides analytics data for the entry system, including the total number of users, counts of users inside campus and concert hall, and the breakdown by roles (students, VIPs, faculty), including paid students.

- **Response**:

  - **Successful Response**:

    ```json
    {
      "success": true,
      "message": "Analytics data fetched successfully",
      "data": {
        "total_users": 1000,
        "inside_campus": 500,
        "inside_concert_hall": 200,
        "students_count": 700,
        "vips_count": 50,
        "faculty_count": 150,
        "paid_students_count": 600,
        "students_inside_concert_hall": 150,
        "vips_inside_concert_hall": 30,
        "faculty_inside_concert_hall": 20
      }
    }
    ```

  - **Error Response**:
    ```json
    {
      "success": false,
      "message": "Error message here"
    }
    ```

### 10. **Dynamic QR Code Validation API**

- **Endpoint**: `/api/entrysystem/validate_dynamic_qr/`
- **Method**: `POST`
- **Permission**: None
- **Description**: Validates a dynamic QR code for entry or exit with a number of people.
- **Request**:
  - **Body**:
    ```json
    {
      "qr_code": "dynamic-qr-code-object-id",
      "mode": "entry",
      "number": 5
    }
    ```
- **Response**:
  - **Entry Approved**:
    ```json
    {
      "success": true,
      "message": "Entry approved",
      "data": {
        "entered_ppl": 1,
        "vip": true
      }
    }
    ```
  - **Duplicate Entry**:
    ```json
    {
      "success": false,
      "message": "Duplicate entry detected"
    }
    ```

---
