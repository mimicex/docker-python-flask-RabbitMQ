#!/usr/bin/env python3
import jwt, json, uuid, pytz
from flask        import Flask, request, jsonify
from functools    import wraps
from datetime     import datetime
from decouple     import config
from lib.rabbitMQ import RabbitMQClient
from lib.task     import TaskClient

# 設定台北時區
taipeiTz = pytz.timezone('Asia/Taipei')
# 設定 task
taskClient = TaskClient()

# 設定 RabbitMQ
rabbitMQClient = RabbitMQClient(
    host=config('RABBITMQ_HOST'),
    port=config('RABBITMQ_PORT'),
    username=config('RABBITMQ_USER'),
    password=config('RABBITMQ_PASSWORD'),
    queue=config('RABBITMQ_QUEUE')
)
rabbitMQClient.connect()
app = Flask(__name__)
app.config['SECRET_KEY'] = config('secretKey')

# JWT token 驗證
def tokenRequired(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            token = token.split(' ')[1]  # Bearer token
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            #print(data['exp'], ' ', datetime.utcnow().timestamp())
            if data == None:
                return jsonify({'error': 'Token is missing'}), 401
            if data['type'] != 'access':
                return jsonify({'error': 'Invalid token'}), 401
            if data['exp'] < datetime.utcnow().timestamp():
                return jsonify({'error': 'Token expired'}), 401
            if int(data['user_id']) == 0:
                return jsonify({'error': 'Invalid token'}), 401
        except:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    return decorated

###
### def createTask
###
### @todo   : 建立任務
###
### @param  : url: str
###
@app.route('/v1/tasks', methods=['POST'])
@tokenRequired
def createTask():
    data = request.json

    if not data or 'kind' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    currentTime = datetime.now(taipeiTz)

    taskId = str(uuid.uuid4())
    task = {
        'taskId'    : taskId,
        'status'    : 'queued',
        'createdAt' : currentTime.isoformat(),
        'config'    : data
    }
    # 發送任務到 Pub/Sub
    # 發送任務到 RabbitMQ
    rabbitMQClient.send(taskId)
    print(f" [x] Sent {taskId}")

    # 設定任務到 Redis
    tasksDb = taskClient.getTask()
    tasksDb[taskId] = task
    taskClient.setTask(json.dumps(tasksDb))

    return jsonify({
        'taskId'    : taskId,
        'status'    : 'queued',
        'createdAt' : task['createdAt']
    }), 201

###
### def getResults
###
### @todo   : 取得任務結果
###
### @param  : taskId: str
###
@app.route('/v1/tasks/<taskId>/results', methods=['GET'])
@tokenRequired
def getResults(taskId):
    tasksDb = taskClient.getTask()

    if taskId not in tasksDb:
        return jsonify({'error': 'Task not found'}), 404
    
    task = tasksDb[taskId]
    
    if task['status'] != 'completed':
        return ({
            'taskId'    : taskId,
            'status'    : task['status'],
            'progress'  : {
                'status': task['status']
            }
        })
    
    resultsDb = taskClient.getResult()
    results   = resultsDb.get(taskId, {})

    return jsonify({
        'taskId' : taskId,
        'status' : 'completed',
        'stats'  : results.get('stats', {}),
        'results': results.get('results', [])
    })

###
### def suspendTask
###
### @todo   : 暫停任務
###
### @param  : taskId: str
###
@app.route('/v1/tasks/<taskId>/suspend', methods=['PUT'])
@tokenRequired
def suspendTask(taskId):
    tasksDb = taskClient.getTask()

    if taskId not in tasksDb:
        return jsonify({'error': 'Task not found'}), 404
    
    task = tasksDb[taskId]
    if task['status'] == 'in_progress':
        task['status'] = 'suspended'
        tasksDb[taskId] = task
        taskClient.setTask(json.dumps(tasksDb))
        return jsonify({
            'taskId'       : taskId,
            'status'       : 'suspended',
            'suspended_at' : datetime.utcnow().isoformat()
        })
    
    return jsonify({'error': 'Task cannot be suspended'}), 400
###
### def getTaskStatus
###
### @todo   : 取得任務狀態
###
### @param  : taskId: str
###
### @return : json
###
@app.route('/v1/tasks/<taskId>', methods=['GET'])
@tokenRequired
def getTaskStatus(taskId):
    tasksDb = taskClient.getTask()

    if taskId not in tasksDb:
        return jsonify({'error': 'Task not found'}), 404
    
    task = tasksDb[taskId]
    tasksDb[taskId] = task
    taskClient.setTask(json.dumps(tasksDb))

    return jsonify({
        'taskId'    : taskId,
        'status'    : task['status'],
        'createdAt' : task['createdAt']
    })

if __name__ == '__main__':
    app.run(debug=True)