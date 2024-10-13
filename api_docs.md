### **EventManagement Project API Documentation**

---

### 1. **User Registration API**

- **Endpoint**: `/api/entrysystem/register/`
- **Method**: `POST`
- **Description**: Allows a new user to register by providing email and Firebase UID.
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

---
