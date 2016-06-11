import json

from ..test_base import BaseTwitterAPITestCase


class FollowersResourceTestCase(BaseTwitterAPITestCase):

    def test_get_followers(self):
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

        # testuser3 follows testuser2
        data = {'username': 'testuser2'}
        headers = {'Authorization': '$RMOTR$-U3'}
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
        expected = [
            {'username': 'testuser1', 'uri': '/profile/testuser1'},
            {'username': 'testuser3', 'uri': '/profile/testuser3'},
        ]
        self.assertEqual(followers, expected)

    def test_get_followers_unauthorized(self):
        headers = {'Authorization': 'foobar'}
        response = self.client.get('/followers', headers=headers)
        self.assertEqual(response.status_code, 401)

    def test_get_followers_missing_access_token(self):
        response = self.client.get('/followers')
        self.assertEqual(response.status_code, 401)
