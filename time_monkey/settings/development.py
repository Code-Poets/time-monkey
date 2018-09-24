# pylint: disable=unused-wildcard-import

from .defaults import *  # NOQA  # pylint: disable=wildcard-import

ENVIRONMENT = 'development'

DEBUG = True

SECRET_KEY = '12345abcdef'  # Can be any string

DATABASES['default']['USER']     = 'postgres'
DATABASES['default']['PASSWORD'] = ''
DATABASES['default']['HOST']     = ''
DATABASES['default']['PORT']     = ''
