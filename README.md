# [pyp-w4] Twitter timeline

Today's group work expands the Twitter API with a few new endpoints, including following capabilities and a timeline resource.

## Authentication

The authentication method has changed a bit compared to the previous one. We keep using authentication tokens, but instead of sending tokens in the POST payload, we will be sending them now in the request headers.

```bash
Authorization: <ACCESS_TOKEN>
```

As you will notice, all three new resources are `@auth_only`. That means all of then need the authentication headers to properly work.

## Settings

An important difference compared to the previous GW, is that we are not using SQLite DB any more. For this assignment we will work with an external service called https://mlab.com/. It's MongoDB as a service. We will use a regular MongoDB client to connect the database, but instead of having a server running locally, we will connect to the MLab service.

One of the first things you need to do is to create an account in MLab and set up you own database and users there. Once you have all your authentication information and also the name of your database you can fill the blank variables in `settings.py`.

```python
HOST = None
USERNAME = None
PASSWORD = None
PORT = 13014
DATABASE_NAME = None
```

_Important: Your solution must be posted to Github with your personal MLab settings, because the service is used to run all tests. Don't worry, after we close the PR you can just delete the Database User._

## Friendship resource

_(Inspired by Twitter's Friendship resource: https://dev.twitter.com/rest/reference/post/friendships/create)_

Create a "following relationship" between the authenticated user (provided by the `ACCESS_TOKEN`) and the user identified by `USERNAME`.

```
POST /friendship/
{
  "username": <USERNAME>
}
Authorization: <ACCESS_TOKEN> (header)
>>>
201 Created
```

Delete a "following relationship" (unfollow):

```
DELETE /friendship/
{
  "username": <USERNAME>
}
Authorization: <ACCESS_TOKEN> (header)
>>>
204
```

## Followers resource

Get the list of followers for the authenticated user (provided by `ACCESS_TOKEN`).

```
GET /followers
Authorization: <ACCESS_TOKEN> (header)
>>>
[
    {
      "username": "<USERNAME>",
      "uri": "/profile/<USERNAME>"
    },
    {
      "username": "<USERNAME>",
      "uri": "/profile/<USERNAME>"
    },
    ...
]
```

## Timeline resource

Returns the list of all tweets posted by all users the current user is following. Current user is given by the provided `ACCESS_TOKEN` in the request's headers. Tweets are sorted by creation date in descending order (last tweet on top).

```
GET /timeline
Authorization: <ACCESS_TOKEN> (header)
>>>
[
    {
        'created': '2016-06-11T13:00:10',
        'id': <TWEET_ID>,
        'text': <TWEET_TEXT>,
        'uri': '/tweet/<TWEET_ID>',
        'user_id': <USER_ID>
    },
    ...
]
```
