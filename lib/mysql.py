#!/usr/bin/env python3
import pymysql
import base64
from decouple import config

class MysqlClient:
    def __init__(self, db):
        self.host     = config('dbHostSlave')
        self.type     = 'slave'
        self.user     = config('dbAccount')
        self.password = config('dbPassword')
        self.db       = db if db else config('dbName')

        self.conn = {}
        self.conn[self.type] = pymysql.connect(host=self.host, port=3306, user=self.user, passwd=self.password, db= self.db, charset='utf8')
        self.cursor = {}
        self.cursor[self.type] = self.conn[self.type].cursor()

    def setMaster(self):
        host = config('dbHostMaster')
        self.conn['master'] = pymysql.connect(host=host, port=3306, user=self.user, passwd=self.password, db= self.db, charset='utf8')
        self.type = 'master'
        self.cursor['master'] = self.conn['master'].cursor()

    def insert(self, sql, type = 'slave'):
        self.cursor[type].execute(sql)
        self.conn[type].commit()

    def close(self, type = 'slave'):
        self.cursor[type].close()
        self.conn[type].close()

    def query(self, sql, type = 'slave'):
        self.cursor[type].execute(sql)
        return self.cursor[type].fetchall()

    def update(self, sql, type = 'slave'):
        self.cursor[type].execute(sql)
        self.conn[type].commit()

    def delete(self, sql, type = 'slave'):
        self.cursor[type].execute(sql)
        self.conn[type].commit()

    def rollback(self, type = 'slave'):
        self.conn[type].rollback()