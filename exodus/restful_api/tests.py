# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User

from rest_framework.test import APITestCase

from reports.models import Application, Report, Permission, Apk
from trackers.models import Tracker

DUMMY_HANDLE = 'com.example'


class RestfulApiApplicationTests(APITestCase):
    PATH = '/api/applications'

    def _force_authentication(self):
        user = User.objects.create_user('username', 'Pas$w0rd')
        self.client.force_authenticate(user)

    def test_returns_unauthorized_when_no_auth(self):
        response = self.client.get(self.PATH)
        self.assertEqual(response.status_code, 401)

    def test_returns_empty_json_when_no_applications(self):
        self._force_authentication()
        response = self.client.get(self.PATH)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['applications'], [])

    def test_returns_applications_with_report_last_update(self):
        self._force_authentication()
        report = Report.objects.create(id=1234)
        application = Application.objects.create(
            name='app_name',
            handle='handle',
            report=report
        )

        expected_json = {
            'applications': [
                {
                    'id': application.id,
                    "handle": application.handle,
                    "name": application.name,
                    "creator": "",
                    "downloads": "",
                    "app_uid": "",
                    "icon_phash": "",
                    "report_updated_at": report.updated_at.timestamp()
                },
            ]
        }

        response = self.client.get(self.PATH)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_json)


class RestfulApiSearchHandleDetailsTests(APITestCase):
    PATH = '/api/search/{}/details'.format(DUMMY_HANDLE)

    def _force_authentication(self):
        user = User.objects.create_user('username', 'Pas$w0rd')
        self.client.force_authenticate(user)

    def test_returns_unauthorized_when_no_auth(self):
        response = self.client.get(self.PATH)
        self.assertEqual(response.status_code, 401)

    def test_returns_empty_json_when_no_app(self):
        self._force_authentication()
        response = self.client.get(self.PATH)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_returns_detailed_json_when_one_app(self):
        tracker = Tracker.objects.create(name='Teemo')
        report = Report.objects.create()
        report.found_trackers.set([tracker.id])
        app = Application.objects.create(
            name='app_name',
            handle=DUMMY_HANDLE,
            report=report,
            version="0.1",
            version_code="01234",
        )
        apk = Apk.objects.create(
            application=app,
            name="app_name",
            sum="app_checksum"
        )
        Permission.objects.create(
            application=app,
            name="AREBELONGTOUS"
        )
        Permission.objects.create(
            application=app,
            name="ALLYOURBASE"
        )

        # Not happy with these but report.creation_date doesn't return the correct format
        creation_date = "{}Z".format(report.creation_date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3])
        updated_at = "{}Z".format(report.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3])

        expected_json = [
            {
                'apk_hash': apk.sum,
                'app_name': app.name,
                'handle': app.handle,
                'report': report.id,
                'trackers': [tracker.id],
                'permissions': ["ALLYOURBASE", "AREBELONGTOUS"],
                'uaid': '',
                'created': creation_date,
                'updated': updated_at,
                'version_code': app.version_code,
                'version_name': app.version,
                'icon_hash': '',
                'downloads': '',
                'creator': ''
            }
        ]

        self._force_authentication()
        response = self.client.get(self.PATH)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_json)


class RestfulApiSearchHandleTests(APITestCase):
    PATH = '/api/search/{}'.format(DUMMY_HANDLE)

    def _force_authentication(self):
        user = User.objects.create_user('username', 'Pas$w0rd')
        self.client.force_authenticate(user)

    def test_returns_unauthorized_when_no_auth(self):
        response = self.client.get(self.PATH)
        self.assertEqual(response.status_code, 401)

    def test_returns_empty_json_when_no_app(self):
        self._force_authentication()
        response = self.client.get(self.PATH)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {})

    def test_returns_detailed_json_when_one_app(self):
        tracker = Tracker.objects.create(name='Teemo')
        report = Report.objects.create()
        report.found_trackers.set([tracker.id])
        app = Application.objects.create(
            name='app_name',
            handle=DUMMY_HANDLE,
            report=report,
            version="0.1",
            version_code="01234",
        )
        Apk.objects.create(
            application=app,
            name="app_name",
            sum="app_checksum"
        )
        Permission.objects.create(
            application=app,
            name="AREBELONGTOUS"
        )
        Permission.objects.create(
            application=app,
            name="ALLYOURBASE"
        )

        # Not happy with these but report.creation_date doesn't return the correct format
        creation_date = "{}Z".format(report.creation_date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3])
        updated_at = "{}Z".format(report.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3])

        expected_json = {
            str(app.handle): {
                'name': app.name,
                'creator': "",
                'reports': [
                    {
                        "id": report.id,
                        "updated_at": updated_at,
                        "creation_date": creation_date,
                        "version": app.version,
                        "version_code": app.version_code,
                        "downloads": "",
                        "trackers": [tracker.id],
                    }
                ]
            }
        }

        self._force_authentication()
        response = self.client.get(self.PATH)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_json)


class RestfulApiTrackersTests(APITestCase):
    PATH = '/api/trackers'

    def test_returns_empty_json_when_no_trackers(self):
        response = self.client.get(self.PATH)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['trackers'], {})

    def test_returns_one_tracker(self):
        tracker = Tracker.objects.create(
            name='Teemo',
            description='bad tracker',
            code_signature='com.teemo',
            network_signature='teemo.com',
            website='https://www.teemo.com'
        )

        expected_json = {
            str(tracker.id): {
                'id': tracker.id,
                'name': tracker.name,
                'description': tracker.description,
                'creation_date': tracker.creation_date.strftime("%Y-%m-%d"),
                'code_signature': tracker.code_signature,
                'network_signature': tracker.network_signature,
                'website': tracker.website
            }
        }

        response = self.client.get(self.PATH)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['trackers'], expected_json)


class RestfulApiReportTests(APITestCase):
    PATH = '/api/report/1234/'

    def _force_authentication(self):
        user = User.objects.create_user('username', 'Pas$w0rd')
        self.client.force_authenticate(user)

    def test_returns_unauthorized_when_no_auth(self):
        response = self.client.get(self.PATH)
        self.assertEqual(response.status_code, 401)

    def test_returns_one_report_infos(self):
        self._force_authentication()
        report = Report.objects.create(id=1234)
        app = Application.objects.create(
            name='app_name',
            handle=DUMMY_HANDLE,
            report=report
        )

        response = self.client.get(self.PATH)
        expected_json = {
            "creation_date": report.creation_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "report_id": report.id,
            "handle": app.handle,
            "apk_dl_link": "",
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_json)

    def test_returns_not_found_when_no_report(self):
        self._force_authentication()

        response = self.client.get(self.PATH)
        self.assertEqual(response.status_code, 404)


class RestfulApiApkTests(APITestCase):
    PATH = '/api/apk/1/'

    def _force_authentication(self):
        user = User.objects.create_user('user', 'Pas$w0rd')
        self.client.force_authenticate(user)

    def _force_admin_authentication(self):
        user = User.objects.create_superuser('user', 'user@mail', 'Pas$w0rd')
        self.client.force_authenticate(user)

    def test_returns_unauthorized_when_no_auth(self):
        response = self.client.get(self.PATH)
        self.assertEqual(response.status_code, 401)

    def test_returns_forbidden_when_no_admin_auth(self):
        self._force_authentication()

        response = self.client.get(self.PATH)
        self.assertEqual(response.status_code, 403)

    def test_returns_not_found_when_no_apk(self):
        self._force_admin_authentication()

        response = self.client.get(self.PATH)
        self.assertEqual(response.status_code, 404)


class RestfulApiReportDetails(APITestCase):
    PATH = '/api/report/1234/details'

    def _force_authentication(self):
        user = User.objects.create_user('user', 'Pas$w0rd')
        self.client.force_authenticate(user)

    def test_returns_unauthorized_when_no_auth(self):
        response = self.client.get(self.PATH)
        self.assertEqual(response.status_code, 401)

    def test_returns_not_found_when_no_report(self):
        self._force_authentication()

        response = self.client.get(self.PATH)
        self.assertEqual(response.status_code, 404)

    def test_returns_detailed_json_when_one_report(self):
        self._force_authentication()

        tracker = Tracker.objects.create(
            name='Teemo',
            description='bad tracker',
            code_signature='com.teemo',
            network_signature='teemo.com',
            website='https://www.teemo.com'
        )
        report = Report.objects.create(id=1234)
        report.found_trackers.set([tracker.id])
        app = Application.objects.create(
            id=1234,
            name='app_name',
            handle=DUMMY_HANDLE,
            report=report,
            version="0.1",
            version_code="01234",
        )
        Apk.objects.create(
            application=app,
            name="app_name",
            sum="app_checksum"
        )
        Permission.objects.create(
            application=app,
            name="AREBELONGTOUS"
        )
        Permission.objects.create(
            application=app,
            name="ALLYOURBASE"
        )

        expected_json = {
            'creation_date': report.creation_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            'found_trackers': [
                {
                    'id': tracker.id,
                    'name': tracker.name,
                    'description': tracker.description,
                    'creation_date': tracker.creation_date.strftime("%Y-%m-%d"),
                    'code_signature': tracker.code_signature,
                    'network_signature': tracker.network_signature,
                    'website': tracker.website
                },
            ],
            'application': {
                'id': app.id,
                'handle': app.handle,
                'name': app.name,
                'creator': '',
                'downloads': '',
                'version': app.version,
                'version_code': app.version_code,
                'icon_path': '',
                'app_uid': '',
                'icon_phash': '',
                'report': report.id,
            }
        }
        response = self.client.get(self.PATH)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_json)
