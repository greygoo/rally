# Copyright 2013: Mirantis Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os

import mock
from six import moves

from rally.cli import envutils
from rally import exceptions
from tests.unit import test


class EnvUtilsTestCase(test.TestCase):

    def test_default_from_global(self):

        @envutils.default_from_global("test_arg_name",
                                      "test_env_name",
                                      "test_missing_arg")
        def test_function(test_arg_name=None):
            pass

        with mock.patch("sys.stdout",
                        new_callable=moves.StringIO) as mock_stdout:
            test_function()
            self.assertEqual(mock_stdout.getvalue(),
                             "Missing argument: --test_missing_arg\n")

    @mock.patch.dict(os.environ,
                     values={envutils.ENV_DEPLOYMENT: "my_deployment_id"},
                     clear=True)
    def test_get_deployment_id_in_env(self):
        deployment_id = envutils.get_global(envutils.ENV_DEPLOYMENT)
        self.assertEqual("my_deployment_id", deployment_id)

    @mock.patch.dict(os.environ, values={}, clear=True)
    @mock.patch("rally.cli.envutils.fileutils.load_env_file")
    def test_get_deployment_id_with_exception(self, mock_load_env_file):
        self.assertRaises(exceptions.InvalidArgumentsException,
                          envutils.get_global, envutils.ENV_DEPLOYMENT, True)
        mock_load_env_file.assert_called_once_with(os.path.expanduser(
            "~/.rally/globals"))

    @mock.patch.dict(os.environ, values={}, clear=True)
    @mock.patch("rally.cli.envutils.fileutils.load_env_file")
    def test_get_deployment_id_with_none(self, mock_load_env_file):
        self.assertIsNone(envutils.get_global(envutils.ENV_DEPLOYMENT))
        mock_load_env_file.assert_called_once_with(os.path.expanduser(
            "~/.rally/globals"))

    @mock.patch.dict(os.environ, values={envutils.ENV_TASK: "my_task_id"},
                     clear=True)
    def test_get_task_id_in_env(self):
        self.assertEqual("my_task_id", envutils.get_global(envutils.ENV_TASK))

    @mock.patch.dict(os.environ, values={}, clear=True)
    @mock.patch("rally.cli.envutils.fileutils.load_env_file")
    def test_get_task_id_with_exception(self, mock_load_env_file):
        self.assertRaises(exceptions.InvalidArgumentsException,
                          envutils.get_global, envutils.ENV_TASK, True)
        mock_load_env_file.assert_called_once_with(os.path.expanduser(
            "~/.rally/globals"))

    @mock.patch.dict(os.environ, values={}, clear=True)
    @mock.patch("rally.cli.envutils.fileutils.load_env_file")
    def test_get_task_id_with_none(self, mock_load_env_file):
        self.assertIsNone(envutils.get_global("RALLY_TASK"))
        mock_load_env_file.assert_called_once_with(os.path.expanduser(
            "~/.rally/globals"))

    @mock.patch.dict(os.environ,
                     values={envutils.ENV_DEPLOYMENT: "test_deployment_id"},
                     clear=True)
    @mock.patch("os.path.exists")
    @mock.patch("rally.cli.envutils.fileutils.update_env_file",
                return_value=True)
    def test_clear_global(self, mock_update_env_file, mock_path_exists):
        envutils.clear_global(envutils.ENV_DEPLOYMENT)
        mock_update_env_file.assert_called_once_with(os.path.expanduser(
            "~/.rally/globals"), envutils.ENV_DEPLOYMENT, "\n")
        self.assertEqual(os.environ, {})

    @mock.patch.dict(os.environ,
                     values={envutils.ENV_DEPLOYMENT: "test_deployment_id",
                             envutils.ENV_TASK: "test_task_id"},
                     clear=True)
    @mock.patch("os.path.exists")
    @mock.patch("rally.cli.envutils.fileutils.update_env_file",
                return_value=True)
    def test_clear_env(self, mock_update_env_file, mock_path_exists):
        envutils.clear_env()
        self.assertEqual(os.environ, {})

    @mock.patch.dict(os.environ, {"OS_AUTH_URL": "fake_auth_url",
                                  "OS_USERNAME": "fake_username",
                                  "OS_PASSWORD": "fake_password",
                                  "OS_TENANT_NAME": "fake_tenant_name",
                                  "OS_REGION_NAME": "fake_region_name",
                                  "OS_ENDPOINT": "fake_endpoint",
                                  "OS_INSECURE": "True",
                                  "OS_CACERT": "fake_cacert"})
    def test_get_creds_from_env_vars(self):
        expected_creds = {
            "auth_url": "fake_auth_url",
            "admin": {
                "username": "fake_username",
                "password": "fake_password",
                "tenant_name": "fake_tenant_name"
            },
            "endpoint": "fake_endpoint",
            "region_name": "fake_region_name",
            "https_cacert": "fake_cacert",
            "https_insecure": True
        }
        creds = envutils.get_creds_from_env_vars()
        self.assertEqual(expected_creds, creds)

    @mock.patch.dict(os.environ, {"OS_AUTH_URL": "fake_auth_url",
                                  "OS_PASSWORD": "fake_password",
                                  "OS_REGION_NAME": "fake_region_name",
                                  "OS_ENDPOINT": "fake_endpoint",
                                  "OS_INSECURE": "True",
                                  "OS_CACERT": "fake_cacert"})
    def test_get_creds_from_env_vars_when_required_vars_missing(self):
        self.assertRaises(exceptions.ValidationError,
                          envutils.get_creds_from_env_vars)
