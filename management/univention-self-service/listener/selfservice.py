#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Univention LDAP
"""listener script to set umc/self-service/passwordreset/email/webserver_address."""
#
# Like what you see? Join us!
# https://www.univention.com/about-us/careers/vacancies/
#
# Copyright 2017-2023 Univention GmbH
#
# https://www.univention.de/
#
# All rights reserved.
#
# The source code of this program is made available
# under the terms of the GNU Affero General Public License version 3
# (GNU AGPL V3) as published by the Free Software Foundation.
#
# Binary versions of this program provided by Univention to you as
# well as other copyrighted, protected or trademarked materials like
# Logos, graphics, fonts, specific documentations and configurations,
# cryptographic keys etc. are subject to a license agreement between
# you and Univention and not subject to the GNU AGPL V3.
#
# In the case you use this program under the terms of the GNU AGPL V3,
# the program is provided in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License with the Debian GNU/Linux or Univention distribution in file
# /usr/share/common-licenses/AGPL-3; if not, see
# <https://www.gnu.org/licenses/>.

from __future__ import absolute_import, annotations

from typing import Dict, List

import univention.config_registry

import listener


description = 'Set umc/self-service/passwordreset/email/webserver_address.'
filter = '(univentionService=univention-self-service)'

UCRV = 'umc/self-service/passwordreset/email/webserver_address'


def handler(dn: str, new: Dict[str, List[bytes]], old: Dict[str, List[bytes]]) -> None:
    if new:
        ucr = univention.config_registry.ConfigRegistry()
        ucr.load()
        if not ucr.get(UCRV):
            fqdn = '%s.%s' % (new['cn'][0].decode('UTF-8'), new.get('associatedDomain')[0].decode('ASCII'))
            listener.setuid(0)
            try:
                univention.config_registry.handler_set(['%s=%s' % (UCRV, fqdn)])
            finally:
                listener.unsetuid()
