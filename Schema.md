
# Schema

### Users Collection

```json
{
    "email": "String", // "required during reg"
    "firebaseUID": "String", //"required" during reg
    "profileDetails": {
      "name": "String",
      "college": "String",
      "phoneNumber": "String",
      "imageURL": "String" , 
      "collegeID" : "String" ,
      "collegeIdUrl" : "String"
    },
    "paymentStatus": true , false,  //default "false"
    "createdAt": "Date",
    "updatedAt": "Date"
}

//this response generates _id which links other collections as userID
```

### Payment Collection

```json
{
    "userId": "ObjectId",  // Reference to user._id
    "amount": "Number",
    "paymentMethod": "String",  // e.g., 'Credit Card', 'PayPal'
    "status": "String",  // 'Pending', 'Completed', or 'Failed'
    "createdAt": "Date" ,
    "updatedAt": "Date"


}

```



### qrData Collection

```json
{
    "userId": "ObjectId",  // Reference to user._id
    "qrUrl": "String",
    "code": "String", // code inside qr , usually userID itself
    "createdAt": "Date",
    "updatedAt": "Date"
}

```


### entryExit Collection

```json
{
    "userId": "ObjectId",  // Reference to user._id
    "currentStatus" : "bool" ,
    "code": "Number",
    "frequencyEntry" : 0 ,
    "frequencyExit" :0 ,
    "vip" : "bool"
    "createdAt" : "Date" ,
    "updatedAt" : "Date" ,

}

```



