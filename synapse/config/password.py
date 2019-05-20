# -*- coding: utf-8 -*-
# Copyright 2015-2016 OpenMarket Ltd
# Copyright 2017-2018 New Vector Ltd
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

from ._base import Config


class PasswordConfig(Config):
    """Password login configuration
    """

    def read_config(self, config):
        password_config = config.get("password_config", {})
        if password_config is None:
            password_config = {}

        self.password_enabled = password_config.get("enabled", True)
        self.password_pepper = password_config.get("pepper", "")

        # Password policy
        self.password_policy = password_config.get("policy", {})
        self.password_policy_enabled = self.password_policy.pop("enabled", False)

    def default_config(self, config_dir_path, server_name, **kwargs):
        return """\
        password_config:
           # Uncomment to disable password login
           #
           #enabled: false

           # Uncomment and change to a secret random string for extra security.
           # DO NOT CHANGE THIS AFTER INITIAL SETUP!
           #
           #pepper: "EVEN_MORE_SECRET"

           # Password policy.
           #
           #policy:
           #  enabled: true
           #  minimum_length: 15
           #  require_digit: true
           #  require_symbol: true
           #  require_lowercase: true
           #  require_uppercase: true
        """
