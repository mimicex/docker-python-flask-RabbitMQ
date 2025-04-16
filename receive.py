#!/usr/bin/env python3
import json, threading, pytz
from datetime           import datetime, timedelta
from decouple           import config
from lib.rabbitMQ       import RabbitMQClient
from lib.mysql          import MysqlClient
from lib.course.course  import CourseClient
from datetime           import datetime, timedelta
from lib.task           import TaskClient

# 設定台北時區
taipeiTz = pytz.timezone('Asia/Taipei')
# 設定任務
taskClient = TaskClient()
# 設定 RabbitMQ 連線
rabbitMQClient = RabbitMQClient(
    host=config('RABBITMQ_HOST'),
    port=config('RABBITMQ_PORT'),
    username=config('RABBITMQ_USER'),
    password=config('RABBITMQ_PASSWORD'),
    queue=config('RABBITMQ_QUEUE')
)
rabbitMQClient.connect()

def runTask(taskId, config):
    tasksDb = taskClient.getTask()
    tasksDb = tasksDb if tasksDb else {}
    # 更新任務狀態
    tasksDb[taskId]['status'] = 'in_progress'
    taskClient.setTask(json.dumps(tasksDb))

    # 處理你要任務 ##############################

    ########################################


    # 更新任務狀態
    resultsDb = taskClient.getResult()
    resultsDb = resultsDb if resultsDb else {}

    currentTime = datetime.now(taipeiTz)
    
    resultsDb[taskId] = {
        'results': '',
        'stats': {
            'start_time' : tasksDb[taskId]['createdAt'],
            'end_time'   : currentTime.isoformat()
        }
    }

    taskClient.setResult(json.dumps(resultsDb))
    tasksDb[taskId]['status'] = 'completed'
    taskClient.setTask(json.dumps(tasksDb))

    mysqlClient = MysqlClient(db='test')
    mysqlClient.setMaster()

    taskData = json.dumps(tasksDb[taskId])
    sqlUpdate = f"UPDATE task_queue SET task_data = '{taskData}' WHERE task_id = '{taskId}'"
    try:
        mysqlClient.update(sqlUpdate)
    except Exception as e:
        mysqlClient.rollback()
        print(e)
    
    taskClient.deleteTask(taskId)

def insertQueueDb(taskId):
    # 取得任務
    tasksDb = taskClient.getTask()

    if taskId not in tasksDb:
        print('taskId not in tasksDb')
        return

    task = tasksDb[taskId]

    config = task['config']['config']
    threading.Thread(target=runTask, args=(taskId, config)).start()

    taskData = json.dumps(task)
    # 將任務資料插入資料庫
    # 流水號	: id
    # 任務編號	: task_id
    # 任務資料	: task_data
    # 新增時間  : YYYY-mm-dd HH:ii:ss	

    # 設定台北時區
    currentTime = datetime.now(taipeiTz)
    deleteTime  = (currentTime + timedelta(days=8)).isoformat()
    # 將任務資料插入資料庫
    sql = f"""
    INSERT INTO test.task_queue(`task_id`, `task_data`, `delete_time`, `ins_time`, `upd_adm_id`) VALUES ('{taskId}', '{taskData}', '{deleteTime}', '{currentTime.isoformat()}', '0')
    """
    mysqlClient = MysqlClient(db='test')
    try:
        mysqlClient.insert(sql)
        mysqlClient.close()
    except Exception as e:
        mysqlClient.rollback()
        print(e)
    return

def callback(ch, method, properties, body):
    try:
        taskId = body.decode("utf-8")
        print(f" [x] Received taskId: {taskId}")
        insertQueueDb(taskId=taskId)
        # 確認訊息已被處理
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Error processing message: {e}")
        # 如果處理失敗，拒絕訊息並重新排隊
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def main():
    try:
        # 設定每次只處理一個訊息
        rabbitMQClient.channel.basic_qos(prefetch_count=1)

        # 設定消費者
        rabbitMQClient.channel.basic_consume(
            queue=config('rabbitMQQueue'),
            on_message_callback=callback
        )

        print(' [*] Waiting for messages. To exit press CTRL+C')
        rabbitMQClient.channel.start_consuming()
    except KeyboardInterrupt:
        print("\nShutting down...")
        rabbitMQClient.channel.stop_consuming()
    finally:
        rabbitMQClient.disconnect()

if __name__ == "__main__":
    main()


