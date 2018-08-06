import os
import sqlite3
import logging

from appdirs import user_data_dir

from .interfaces import StoreInterface

log = logging.getLogger(__name__)
timeformat = "%Y%m%d-%H%M%S"


class SQLiteFile():
    """ This class ensures that the user's data is stored in its OS
        preotected user directory:

        **OSX:**

         * `~/Library/Application Support/<AppName>`

        **Windows:**

         * `C:\\Documents and Settings\\<User>\\Application Data\\Local Settings\\<AppAuthor>\\<AppName>`
         * `C:\\Documents and Settings\\<User>\\Application Data\\<AppAuthor>\\<AppName>`

        **Linux:**

         * `~/.local/share/<AppName>`

         Furthermore, it offers an interface to generated backups
         in the `backups/` directory every now and then.

         .. note:: The file name can be overwritten when providing a keyword
            argument ``profile``.
    """

    appname = "bitshares"
    appauthor = "Fabian Schuh"
    data_dir = user_data_dir(appname, appauthor)

    def __init__(self, *args, **kwargs):
        if "profile" in kwargs:
            self.storageDatabase = "{}.sqlite".format(kwargs["profile"])
        else:
            self.storageDatabase = "bitshares.sqlite"

        self.sqlDataBaseFile = os.path.join(self.data_dir, self.storageDatabase)

        """ Ensure that the directory in which the data is stored
            exists
        """
        if os.path.isdir(self.data_dir):
            return
        else:
            try:
                os.makedirs(self.data_dir)
            except FileExistsError:
                return
            except OSError:
                raise


class SQLiteStore(SQLiteFile, StoreInterface):

    __tablename__ = None
    __key__ = None
    __value__ = None

    def __init__(self, *args, **kwargs):
        #: Storage
        SQLiteFile.__init__(self, *args, **kwargs)
        if not self.exists():
            self.create()

    def _haveKey(self, key):
        """ Is the key `key` available?
        """
        query = (
            "SELECT {} FROM {} WHERE {}=?".format(
                self.__value__,
                self.__tablename__,
                self.__key__
            ), (key,))
        connection = sqlite3.connect(self.sqlDataBaseFile)
        cursor = connection.cursor()
        cursor.execute(*query)
        return True if cursor.fetchone() else False

    def __setitem__(self, key, value):
        """ Sets an item in the store
        """
        if self._haveKey(key):
            query = (
                "UPDATE {} SET {}=? WHERE {}=?".format(
                    self.__tablename__,
                    self.__value__,
                    self.__key__
                ), (value, key))
        else:
            query = (
                "INSERT INTO {} ({}, {}) VALUES (?, ?)".format(
                    self.__tablename__,
                    self.__key__,
                    self.__value__,
            ), (key, value))
        connection = sqlite3.connect(self.sqlDataBaseFile)
        cursor = connection.cursor()
        cursor.execute(*query)
        connection.commit()

    def __getitem__(self, key):
        """ Gets an item from the store as if it was a dictionary
        """
        query = (
            "SELECT {} FROM {} WHERE {}=?".format(
                self.__value__,
                self.__tablename__,
                self.__key__
            ), (key,))
        connection = sqlite3.connect(self.sqlDataBaseFile)
        cursor = connection.cursor()
        cursor.execute(*query)
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            if key in self.defaults:
                return self.defaults[key]
            else:
                return None

    def __iter__(self):
        """ Iterates through the store
        """
        return iter(self.items())

    def __len__(self):
        """ return lenght of store
        """
        query = ("SELECT id from {}".format(self.__tablename__))
        connection = sqlite3.connect(self.sqlDataBaseFile)
        cursor = connection.cursor()
        cursor.execute(query)
        return len(cursor.fetchall())

    def __contains__(self, key):
        """ Tests if a key is contained in the store.

            May test againsts self.defaults
        """
        if self._haveKey(key) or key in self.defaults:
            return True
        else:
            return False

    def items(self):
        """ returns all items off the store as tuples
        """
        query = ("SELECT {}, {} from {}".format(
            self.__key__,
            self.__value__,
            self.__tablename__))
        connection = sqlite3.connect(self.sqlDataBaseFile)
        cursor = connection.cursor()
        cursor.execute(query)
        r = []
        for key, value in cursor.fetchall():
            r.append((key, value))
        return r

    def get(self, key, default=None):
        """ Return the key if exists or a default value
        """
        if key in self:
            return self.__getitem__(key)
        else:
            return default

    # Specific for this library
    def delete(self, key):
        """ Delete a key from the store
        """
        query = (
            "DELETE FROM {} WHERE {}=?".format(
                self.__tablename__,
                self.__key__
            ), (key,))
        connection = sqlite3.connect(self.sqlDataBaseFile)
        cursor = connection.cursor()
        cursor.execute(*query)
        connection.commit()

    def wipe(self):
        """ Wipe the store
        """
        query = "DELETE FROM {}".format(self.__tablename__)
        connection = sqlite3.connect(self.sqlDataBaseFile)
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()

    def exists(self):
        """ Check if the database table exists
        """
        query = ("SELECT name FROM sqlite_master " +
                 "WHERE type='table' AND name=?",
                 (self.__tablename__, ))
        connection = sqlite3.connect(self.sqlDataBaseFile)
        cursor = connection.cursor()
        cursor.execute(*query)
        return True if cursor.fetchone() else False

    def create(self):
        """ Create the new table in the SQLite database
        """
        query = (
            """
            CREATE TABLE {} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                {} STRING(256),
                {} STRING(256)
            )"""
        ).format(
            self.__tablename__,
            self.__key__,
            self.__value__
        )
        connection = sqlite3.connect(self.sqlDataBaseFile)
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
