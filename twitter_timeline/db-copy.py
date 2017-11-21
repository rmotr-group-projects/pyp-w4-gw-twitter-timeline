
Collection: auth    (3 docs)

{
    "_id": {
        "$oid": "5952efd54c8e0838c46d7e55"
    },
    "access_token": "$RMOTR$-U1",
    "user_id": {
        "$oid": "575b5c2bab63bca09af707a5"
    }
}


Collection: tweets  (6 docs)

{
    "_id": {
        "$oid": "575b5d00ab63bca12dc5c883"
    },
    "content": "Tweet 1 testuser1",
    "user_id": {
        "$oid": "575b5c2bab63bca09af707a5"
    },
    "created": {
        "$date": "2016-06-11T12:00:00.000Z"
    }
}


Collection: users  (3 docs)

{
    "_id": {
        "$oid": "575b5c2bab63bca09af707a5"
    },
    "username": "testuser1",
    "first_name": "Test",
    "last_name": "User",
    "birth_date": "2016-01-30",
    "password": "022c0b524a0258fc73d5ce9bcb0e5aa2"
}


Collection: system.indexes  (3 docs)

{
    "v": 1,
    "key": {
        "_id": 1
    },
    "name": "_id_",
    "ns": "twitter-timeline.users"
}