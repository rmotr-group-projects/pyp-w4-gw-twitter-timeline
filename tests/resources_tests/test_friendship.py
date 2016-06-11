import json

from ..test_base import BaseTwitterAPITestCase


class CreateFriendshipTestCase(BaseTwitterAPITestCase):

    def test_follow_user(self):
        # Preconditions
        headers = {'Authorization': '$RMOTR$-U2'}
        response = self.client.get('/followers', headers=headers)
        followers = json.loads(response.data.decode(response.charset))
        self.assertEqual(followers, [])

        # testuser1 follows testuser2
        data = {'username': 'testuser2'}
        headers = {'Authorization': '$RMOTR$-U1'}
        response = self.client.post(
            '/friendship',
            data=json.dumps(data),
            headers=headers,
            content_type='application/json')
        self.assertEqual(response.status_code, 201)

        # Postconditions
        headers = {'Authorization': '$RMOTR$-U2'}
        response = self.client.get('/followers', headers=headers)
        followers = json.loads(response.data.decode(response.charset))
        expected = [{'username': 'testuser1', 'uri': '/profile/testuser1'}]
        self.assertEqual(followers, expected)

    def test_follow_invalid_target_usernamae(self):
        data = {'username': 'foobar'}
        headers = {'Authorization': '$RMOTR$-U1'}
        response = self.client.post(
            '/friendship',
            data=json.dumps(data),
            headers=headers,
            content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_follow_not_authenticated(self):
        data = {'username': 'testuser2'}
        headers = {'Authorization': 'foobar'}
        response = self.client.post(
            '/friendship',
            data=json.dumps(data),
            headers=headers,
            content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_follow_missing_username(self):
        headers = {'Authorization': '$RMOTR$-U1'}
        response = self.client.post(
            '/friendship',
            data=json.dumps({}),
            headers=headers,
            content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_follow_missing_access_token(self):
        data = {'username': 'testuser2'}
        response = self.client.post(
            '/friendship',
            data=json.dumps(data),
            # missing Authorization header
            content_type='application/json')
        self.assertEqual(response.status_code, 401)


class DeleteFriendshipTestCase(BaseTwitterAPITestCase):

    def setUp(self):
        super(DeleteFriendshipTestCase, self).setUp()

        headers = {'Authorization': '$RMOTR$-U1'}
        self.client.post(
            '/friendship',
            data=json.dumps({
                'username': 'testuser2'
            }),
            headers=headers,
            content_type='application/json')

    def test_unfollow_user(self):
        # Preconditions
        headers = {'Authorization': '$RMOTR$-U2'}
        response = self.client.get('/followers', headers=headers)
        followers = json.loads(response.data.decode(response.charset))
        expected = [{'username': 'testuser1', 'uri': '/profile/testuser1'}]
        self.assertEqual(followers, expected)

        # testuser1 unfollows testuser2
        headers = {'Authorization': '$RMOTR$-U1'}
        response = self.client.delete(
            '/friendship',
            data=json.dumps({
                'username': 'testuser2'
            }),
            headers=headers,
            content_type='application/json')
        self.assertEqual(response.status_code, 204)

        # Postconditions
        headers = {'Authorization': '$RMOTR$-U2'}
        response = self.client.get('/followers', headers=headers)
        followers = json.loads(response.data.decode(response.charset))
        self.assertEqual(followers, [])
