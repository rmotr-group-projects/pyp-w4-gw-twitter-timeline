import json

from ..test_base import BaseTwitterAPITestCase


class TimelineResourceTestCase(BaseTwitterAPITestCase):

    def setUp(self):
        super(TimelineResourceTestCase, self).setUp()
        self.db.followers.remove({})
        headers = {'Authorization': '$RMOTR$-U1'}
        self.client.post(
            '/friendship',
            data=json.dumps({
                'username': 'testuser2'
            }),
            headers=headers,
            content_type='application/json')

    def test_user_timeline_one_follower(self):
        headers = {'Authorization': '$RMOTR$-U1'}
        response = self.client.get('/timeline', headers=headers)
        self.assertEqual(response.status_code, 200)
        expected = [
            {
                u'text': u'Tweet 3 testuser2',
                u'uri': u'/tweet/575b5d00ab63bca12dc5c887',
                u'user_id': u'575b5c2bab63bca09af707a4',
                u'id': u'575b5d00ab63bca12dc5c887',
                u'created': u'2016-06-11 13:00:10'
            },
            {
                u'text': u'Tweet 2 testuser2',
                u'uri': u'/tweet/575b5d00ab63bca12dc5c886',
                u'user_id': u'575b5c2bab63bca09af707a4',
                u'id': u'575b5d00ab63bca12dc5c886',
                u'created': u'2016-06-11 13:00:05'
            },
            {
                u'text': u'Tweet 1 testuser2',
                u'uri': u'/tweet/575b5d00ab63bca12dc5c885',
                u'user_id': u'575b5c2bab63bca09af707a4',
                u'id': u'575b5d00ab63bca12dc5c885',
                u'created': u'2016-06-11 13:00:00'
            }
        ]
        self.assertEqual(
            json.loads(response.data.decode(response.charset)), expected)


    def test_user_timeline_many_followers(self):
        # testuser1 follows testuser3
        headers = {'Authorization': '$RMOTR$-U1'}
        self.client.post(
            '/friendship',
            data=json.dumps({'username': 'testuser3'}),
            headers=headers,
            content_type='application/json')

        response = self.client.get('/timeline',
                                   headers=headers)
        self.assertEqual(response.status_code, 200)
        expected = [
            {
                u'text': u'Tweet 3 testuser2',
                u'uri': u'/tweet/575b5d00ab63bca12dc5c887',
                u'user_id': u'575b5c2bab63bca09af707a4', u'id': u'575b5d00ab63bca12dc5c887',
                u'created': u'2016-06-11 13:00:10'
            },
            {
                u'text': u'Tweet 1 testuser3',
                u'uri': u'/tweet/575b5d00ab63bca12dc5c888',
                u'user_id': u'575b5c2bab63bca09af707a3',
                u'id': u'575b5d00ab63bca12dc5c888',
                u'created': u'2016-06-11 13:00:07'
            },
            {
                u'text': u'Tweet 2 testuser2',
                u'uri': u'/tweet/575b5d00ab63bca12dc5c886',
                u'user_id': u'575b5c2bab63bca09af707a4',
                u'id': u'575b5d00ab63bca12dc5c886',
                u'created': u'2016-06-11 13:00:05'
            },
            {
                u'text': u'Tweet 1 testuser2',
                u'uri': u'/tweet/575b5d00ab63bca12dc5c885',
                u'user_id': u'575b5c2bab63bca09af707a4',
                u'id': u'575b5d00ab63bca12dc5c885',
                u'created': u'2016-06-11 13:00:00'
            }
        ]
        self.assertEqual(
            json.loads(response.data.decode(response.charset)), expected)

    def test_user_timeline_no_followings(self):
        headers = {'Authorization': '$RMOTR$-U2'}
        response = self.client.get('/timeline',
                                   headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.data.decode(response.charset)), [])

    def test_user_timeline_not_authenticated(self):
        headers = {'Authorization': 'foobar'}
        response = self.client.get('timeline', headers=headers)
        self.assertEqual(response.status_code, 401)

    def test_user_timeline_missing_access_token(self):
        response = self.client.get('/timeline')
        self.assertEqual(response.status_code, 401)
