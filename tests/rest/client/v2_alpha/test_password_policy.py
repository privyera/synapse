# -*- coding: utf-8 -*-
# Copyright 2019 The Matrix.org Foundation C.I.C.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

from synapse.api.errors import Codes
from synapse.rest.client.v1 import login
from synapse.rest.client.v2_alpha import password_policy, register

from tests import unittest


class PasswordPolicyTestCase(unittest.HomeserverTestCase):
    """Tests the password policy feature and its compliance with MSC2000.

    When validating a password, Synapse does the necessary checks in this order:

        1. Password is long enough
        2. Password contains digit(s)
        3. Password contains symbol(s)
        4. Password contains uppercase letter(s)
        5. Password contains lowercase letter(s)

    Therefore, each test in this test case that tests whether a password triggers the
    right error code to be returned provides a password good enough to pass the previous
    steps but not the one it's testing (nor any step that comes after).
    """

    servlets = [
        login.register_servlets,
        register.register_servlets,
        password_policy.register_servlets,
    ]

    def make_homeserver(self, reactor, clock):
        self.register_url = "/_matrix/client/r0/register"
        self.policy = {
            "enabled": True,
            "minimum_length": 10,
            "require_digit": True,
            "require_symbol": True,
            "require_lowercase": True,
            "require_uppercase": True,
        }

        config = self.default_config()
        config["password_config"] = {
            "policy": self.policy,
        }

        hs = self.setup_test_homeserver(config=config)
        return hs

    def test_get_policy(self):
        """Tests if the /password_policy endpoint returns the configured policy."""

        request, channel = self.make_request("GET", "/_matrix/client/r0/password_policy")
        self.render(request)

        self.assertEqual(channel.code, 200, channel.result)
        self.assertEqual(channel.json_body["m.minimum_length"], 10, channel.result)
        self.assertEqual(channel.json_body["m.require_digit"], True, channel.result)
        self.assertEqual(channel.json_body["m.require_symbol"], True, channel.result)
        self.assertEqual(channel.json_body["m.require_lowercase"], True, channel.result)
        self.assertEqual(channel.json_body["m.require_uppercase"], True, channel.result)

    def test_password_too_short(self):
        request_data = json.dumps({"username": "kermit", "password": "shorty"})
        request, channel = self.make_request("POST", self.register_url, request_data)
        self.render(request)

        self.assertEqual(channel.code, 400, channel.result)
        self.assertEqual(
            channel.json_body["errcode"],
            Codes.PASSWORD_TOO_SHORT,
            channel.result,
        )

    def test_password_no_digit(self):
        request_data = json.dumps({"username": "kermit", "password": "longerpassword"})
        request, channel = self.make_request("POST", self.register_url, request_data)
        self.render(request)

        self.assertEqual(channel.code, 400, channel.result)
        self.assertEqual(
            channel.json_body["errcode"],
            Codes.PASSWORD_NO_DIGIT,
            channel.result,
        )

    def test_password_no_symbol(self):
        request_data = json.dumps({"username": "kermit", "password": "l0ngerpassword"})
        request, channel = self.make_request("POST", self.register_url, request_data)
        self.render(request)

        self.assertEqual(channel.code, 400, channel.result)
        self.assertEqual(
            channel.json_body["errcode"],
            Codes.PASSWORD_NO_SYMBOL,
            channel.result,
        )

    def test_password_no_uppercase(self):
        request_data = json.dumps({"username": "kermit", "password": "l0ngerpassword!"})
        request, channel = self.make_request("POST", self.register_url, request_data)
        self.render(request)

        self.assertEqual(channel.code, 400, channel.result)
        self.assertEqual(
            channel.json_body["errcode"],
            Codes.PASSWORD_NO_UPPERCASE,
            channel.result,
        )

    def test_password_no_lowercase(self):
        request_data = json.dumps({"username": "kermit", "password": "L0NGERPASSWORD!"})
        request, channel = self.make_request("POST", self.register_url, request_data)
        self.render(request)

        self.assertEqual(channel.code, 400, channel.result)
        self.assertEqual(
            channel.json_body["errcode"],
            Codes.PASSWORD_NO_LOWERCASE,
            channel.result,
        )

    def test_password_compliant(self):
        request_data = json.dumps({"username": "kermit", "password": "L0ngerpassword!"})
        request, channel = self.make_request("POST", self.register_url, request_data)
        self.render(request)

        # Getting a 401 here means the password has passed validation and the server has
        # responded with a list of registration flows.
        self.assertEqual(channel.code, 401, channel.result)
