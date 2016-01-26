import requests
from unittest import TestCase

class APIError(Exception):
    pass

class APIModel(object):
    def __init__(self, creds, requester, params):
        self.creds = creds
        self.requester = requester
        self.params = params

    def __getattr__(self, attr):
        try:
            return self.params[attr]
        except:
            raise AttributeError

class Subscriber(APIModel):
    def __repr__(self):
        return '<Subscriber {}>'.format(self.id)

class Form(APIModel):
    def add_subscriber(self, email, first_name):
        resp = self.requester.post(
            '{}{}'.format(self.creds.base_url, 'v3/forms/{}/subscribe'.format(self.id)),
            data={
                'email': email,
                'name': first_name,
                }, params={'api_key': self.creds.api_key})
        if resp.status_code >= 300:
            raise APIError(resp.content)

        return Subscriber(self.creds, self.requester, resp.json()['subscription'])

    def __repr__(self):
        return '<Form:{}>'.format(self.params.get('name', 'Unknown'))

class CredentialsObject(object):
    def __init__(self, api_key, base_url="https://api.convertkit.com/"):
        self.api_key = api_key
        self.base_url = base_url

class Forms(object):
    def __init__(self, creds, requester):
        self.creds = creds
        self.requester = requester

    def list(self):
        resp = self.requester.get(
            '{}{}'.format(self.creds.base_url, 'v3/forms'),
            params={
                'api_key':self.creds.api_key
                })
        if resp.status_code >= 300:
            raise APIError(resp.content)
        return [Form(self.creds, self.requester, x) for x in resp.json()['forms']]


class ConvertKit(object):
    def __init__(self, api_key, base_url="https://api.convertkit.com/", requester=None):
        self.creds = CredentialsObject(api_key, base_url)
        self.requester = requester or requests

    @property
    def forms(self):
        return Forms(self.creds, self.requester)


class FormTestCase(TestCase):
    def test_attrs_accessible_like_object(self):
        f = Form(None, None, {'test': 1})
        self.assertEqual(f.test, 1)

if __name__ == '__main__':
    import os, sys
    from pprint import pprint

    key = os.getenv('CONVERTKIT_API_KEY')
    if not key:
        print("You must specify the CONVERTKIT_API_KEY environment variable")
        sys.exit(1)

    ck = ConvertKit(key)
    forms = ck.forms.list()
    pprint([(x.id, x.name) for x in forms])
