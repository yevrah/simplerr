import os
import sys
from pathlib import Path
from peewee import *


class ConfigBase(object):
    VERSION = "0.1.1"
    NAME = "My App name"
    CWD = Path().cwd()


    DATABASE_PATH =  CWD / 'people.db'
    DATABASE = SqliteDatabase(DATABASE_PATH.absolute().__str__())


class Config(ConfigBase):
    NAME = "SOME OTHER NAME"
