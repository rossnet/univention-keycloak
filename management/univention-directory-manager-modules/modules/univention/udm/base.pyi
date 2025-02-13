# -*- coding: utf-8 -*-
#
# Like what you see? Join us!
# https://www.univention.com/about-us/careers/vacancies/
#
# Copyright 2018-2023 Univention GmbH
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
# you and Univention.
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

from __future__ import absolute_import, unicode_literals

from collections import namedtuple
from typing import Any, Dict, Iterable, Iterator, List, Optional, Text, TypeVar, Union  # noqa: F401

from six import with_metaclass

from .plugins import Plugin


LdapMapping = namedtuple('LdapMapping', ('ldap2udm', 'udm2ldap'))


BaseObjectTV = TypeVar('BaseObjectTV', bound=BaseObject)  # noqa: PYI001
BaseModuleTV = TypeVar('BaseModuleTV', bound=BaseModule)  # noqa: PYI001
BaseModuleMetadataTV = TypeVar('BaseModuleMetadataTV', bound=BaseModuleMetadata)  # noqa: PYI001
BaseObjectPropertiesTV = TypeVar('BaseObjectPropertiesTV', bound=BaseObjectProperties)  # noqa: PYI001


class BaseObjectProperties(object):
    _udm_obj = None  # type: BaseObjectTV

    def __init__(self, udm_obj):  # type: (BaseObjectTV) -> None
        ...

    def __repr__(self):  # type: () -> Text
        ...

    def __deepcopy__(self, memo):  # type: (Dict[int, Dict[Text, Any]]) -> Dict[Text, Any]
        ...


class BaseObject(object):
    dn = ''
    props = None  # type: BaseObjectPropertiesTV
    options = []  # type: List[Text]
    policies = []  # type: List[Text]
    position = ''  # type: Text
    superordinate = None  # type: Text
    _udm_module = None  # type: BaseModuleTV

    def __init__(self):  # type: () -> None
        ...

    def __repr__(self):  # type: () -> Text
        ...

    def reload(self):  # type: () -> BaseObjectTV
        ...

    def save(self):  # type: () -> BaseObjectTV
        ...

    def delete(self, remove_childs=False):  # type: (Optional[bool]) -> None
        ...


class BaseModuleMetadata(object):
    auto_open = True
    auto_reload = True

    def __init__(self, meta):  # type: (BaseModule.Meta) -> None
        self.supported_api_versions = []  # type: Iterable[int]
        self.suitable_for = []  # type: Iterable[Text]
        self.used_api_version = None  # type: int
        self._udm_module = None  # type: BaseModuleTV

    @property
    def identifying_property(self):  # type: () -> Text
        ...

    def lookup_filter(self, filter_s=None):  # type: (Optional[Text]) -> Text
        ...

    @property
    def mapping(self):  # type: () -> LdapMapping
        ...


class ModuleMeta(Plugin):
    udm_meta_class = BaseModuleMetadata

    def __new__(mcs, name, bases, attrs):
        ...


class BaseModule(with_metaclass(ModuleMeta)):
    _udm_object_class = BaseObject
    _udm_module_meta_class = BaseModuleMetadata

    class Meta:
        supported_api_versions = ()  # type: Iterable[int]
        suitable_for = []  # type: Iterable[Text]

    def __init__(self, name, connection, api_version):  # type: (Text, Any, int) -> None
        self.connection = connection  # type: Any
        self.name = name  # type: Text
        self.meta = None  # type: BaseModuleMetadataTV

    def __repr__(self):  # type: () -> Text
        ...

    def new(self, superordinate=None):  # type: (Optional[Union[Text, BaseObjectTV]]) -> BaseObjectTV
        ...

    def get(self, dn):  # type: (Text) -> BaseObjectTV
        ...

    def get_by_id(self, id):  # type: (Text) -> BaseObjectTV
        ...

    def search(self, filter_s='', base='', scope='sub', sizelimit=0):
        # type: (Text, Optional[Text], Optional[Text], int) -> Iterator[BaseObjectTV]
        ...
