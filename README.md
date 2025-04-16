# Python Flask Task Queue RESTful API RabbitMQ + Redis + Mysql

## 使用 JWT TOKEN 驗證，透過 RESTful API 發送任務，取得任務結果，並且可以暫停任務






## 建立 docker image

```
docker build -t rabbit_python:latest .
```

## touch .env

```
touch .env
```

## 修改 .env

``` 
secretKey=建立密鑰
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=建立帳號
RABBITMQ_PASSWORD=建立密碼
RABBITMQ_QUEUE=test
REDIS_PWD=建立密碼
dbHostSlave=
dbAccount=
dbPassword=
dbName=
```

## 建立網路

```
docker network create rabbitMQ_net
```

## 執行 docker container

```
docker-compose up -d
```

## 建立 token

```
python createToken.py
```
## 進入 RabbitMQ

```
docker exec -it rabbitMQ bash
```
## 建立 RabbitMQ queue

```
rabbitmqadmin declare queue --vhost=Some_Virtual_Host name=test durable=true
```

## 進入 RabbitMQ 管理介面

```
http://localhost:15672/
```


## 建立監聽

```
python receive.py
```

## 測試

```
python testCreateTask.py
```
