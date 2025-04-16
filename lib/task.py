#!/usr/bin/env python3
from lib.redis import RedisClient
import json
class TaskClient:
    def __init__(self):
        self.redisClient = RedisClient()
        self.taskKey   = 'tasks_db'
        self.resultKey = 'results_db'
    ###
    ### def getTask
    ###
    ### @todo   : 取得任務
    ###
    ### @param  : url: str
    ###
    def getTask(self):
        tasksDb = self.redisClient.get(self.taskKey)
        tasksDb = tasksDb if tasksDb else {}
        return tasksDb
    ###
    ### def getResult
    ###
    ### @todo   : 取得任務結果
    ###
    ### @param  : url: str
    ###
    def getResult(self):
        resultsDb = self.redisClient.get(self.resultKey)
        resultsDb = resultsDb if resultsDb else {}
        return resultsDb
    ###
    ### def setTask
    ###
    ### @todo   : 設定任務
    ###
    ### @param  : task: str
    ###
    def setTask(self, task):
        self.redisClient.set(self.taskKey, task)
    ###
    ### def setResult
    ###
    ### @todo   : 設定任務結果
    ###
    ### @param  : result: str
    ###
    def setResult(self, result):
        self.redisClient.set(self.resultKey, result)
    ###
    ### def updateTask
    ###
    ### @todo   : 更新任務
    ###
    ### @param  : taskId: str
    ###
    def deleteTask(self, taskId):
        tasksDb = self.getTask()
        tasksDb.pop(taskId)
        self.setTask(json.dumps(tasksDb))