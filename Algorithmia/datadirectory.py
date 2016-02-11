'Algorithmia Data API Client (python)'

import json
import os
import re
import tempfile

import Algorithmia
from Algorithmia.data import datafile

def getUrl(path):
    return '/v1/data/' + path

class DataDirectory(object):
    def __init__(self, client, dataUrl):
        self.client = client
        # Parse dataUrl
        self.path = re.sub(r'^data://|^/', '', dataUrl)
        self.url = getUrl(self.path)

    def exists(self):
        # Heading a directory apparently isn't a valid operation
        response = self.client.getHelper(self.url)
        return (response.status_code == 200)

    def create(self):
        parent, name = self.getParentAndCurrent()
        json = { 'name': name }

        response = self.client.postJsonHelper(getUrl(parent), json, False)
        if (response.status_code != 200):
            raise Exception("Directory creation failed: " + str(response.content))

    def delete(self, force):
        # Delete from data api
        url = self.url
        if force:
            url += '?force=true'

        result = self.client.deleteHelper(url)
        if 'error' in result:
            raise Exception(result['error']['message'])
        else:
            return True

    def file(self, name):
        return datafile(self.client, os.path.join(self.path, name))

    def files(self):
        return self._getDirectoryIterator('files')

    def _getDirectoryIterator(self, key):
        response = self.client.getHelper(self.url)
        if response.status_code != 200:
            raise Exception("Directory iteration failed: " + str(response.content))

        content = json.loads(response.content)
        if content[key]:
            for f in content[key]:
                yield datafile(self.client, os.path.join(self.path, f['filename']))

    def getParentAndCurrent(self):
        parent, rest = os.path.split(self.path)
        while not rest:
            if not parent:
                raise Exception('Invalid directory path')
            parent, rest = os.path.split(parent)

        if not parent:
                raise Exception('Invalid directory path')

        return parent, rest