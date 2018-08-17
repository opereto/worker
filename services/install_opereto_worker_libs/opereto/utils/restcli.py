import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
import json

try:
    requests.packages.urllib3.disable_warnings()
except AttributeError:
    pass
import traceback


class GenericRestClient():

    def __init__(self, user=None, password=None, auth_method='http_digest', timeout=30, **kwargs):
        self.headers = {'content-type': 'application/json; charset=utf-8', 'X-API-Version': '3.0'}
        self.token = {}
        if auth_method=='http_digest':
            print 'Auth method selected: http digest authentication.'
            self.authObj = HTTPDigestAuth(user, password, True)

        elif auth_method=='http_basic':
            print 'Auth method selected: http basic authentication.'
            self.authObj = HTTPBasicAuth(user, password)

        elif auth_method=='bearer':
            print 'Auth method selected: token bearer authentication.'
            self.token = {
                "Authorization": "Bearer {}".format(kwargs['token']),
                'content-type': 'application/json'
            }
            self.authObj=None

        else:
            self.authObj=None

        self.timeout = timeout


    def get(self, requesturl, headers=None, **kwargs):
        headers = headers if headers else self.headers
        return requests.get(requesturl, headers=headers.update(self.token), auth=self.authObj, verify=False, timeout=self.timeout, **kwargs)

    def post(self, requesturl, data={}, files={}, headers=None, **kwargs):
        if files:
            return requests.post(requesturl, files=files, headers=headers, auth=self.authObj, verify=False,timeout=self.timeout, **kwargs)
        else:
            headers = headers if headers else self.headers
            return requests.post(requesturl, data=json.dumps(data), headers=headers.update(self.token), auth=self.authObj, verify=False,timeout=self.timeout, **kwargs)

    def delete(self, requesturl, headers=None, **kwargs):
        headers = headers if headers else self.headers
        return requests.delete(requesturl, headers=headers.update(self.token), auth=self.authObj, verify=False,timeout=self.timeout, **kwargs)

    def put(self, requesturl, data={}, headers=None, **kwargs):
        headers = headers if headers else self.headers
        return requests.put(requesturl, data=json.dumps(data), headers=headers.update(self.token), auth=self.authObj, verify=False,timeout=self.timeout, **kwargs)



