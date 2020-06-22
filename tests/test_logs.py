"""
This tests is a collection of test for check the model and views logs
"""
import os
import tempfile

from django.db import models
from django.test import TestCase
# from django.conf import settings

from djimporter.models import ImportLog

# settings.ROOT_URLCONF = 'djimporter.urls'
# INSTALLED_APPS = ('django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sessions', 'django.contrib.sites', 'django.contrib.staticfiles', 'background_task', 'djimporter', 'tests')

# def pytest_configure():
    # settings.configure(INSTALLED_APPS=INSTALLED_APPS)

class TestLogs(TestCase):

    def setUp(self):
        data = {'id': 1, 'status': ImportLog.CREATED, 'user':"user1", 'input_file': "File_one.csv"}
        self.log = ImportLog.objects.create(**data)

    def test_entrylogs_list(self):
        url = '/logs/'
        # import pdb; pdb.set_trace()
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_entrylog_id(self):
        url = '/logs/1/'
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_entrylog_delete_get(self):
        url = '/logs/1/delete/'
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    # def test_entrylog_delete_post(self):
        # url = '/logs/1/delete/'
        # res = self.client.post(url, data={'pk': 1})
        # self.assertEqual(res.status_code, 200)
