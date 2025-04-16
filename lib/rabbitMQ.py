#!/usr/bin/env python3
import pika

class RabbitMQClient:
    ###
    ### def __init__
    ###
    ### @todo   : 初始化
    ###
    ### @param  : host      : str = ''
    ### @param  : port      : int = 5672
    ### @param  : username  : str = ''
    ### @param  : password  : str = ''
    ### @param  : queue     : str = ''
    ###
    ### @return : void
    ###
    def __init__(self, host: str = '', port: int = 5672, username: str = '', password: str = '', queue: str = ''):
        self.host     = host
        self.port     = port
        self.username = username
        self.password = password
        self.queue    = queue
    ###
    ### def connect
    ###
    ### @todo   : 連接
    ###
    ### @return : void
    ###
    def connect(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, port=self.port, credentials=pika.PlainCredentials(self.username, self.password)))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue, durable=True, arguments={"x-queue-type": "quorum"})
    ###
    ### send
    ###
    ### @todo   : 發送訊息
    ###
    ### @param  : message: str
    ###
    ### @return : void
    ###
    def send(self, message: str):
        self.channel.basic_publish(exchange='', routing_key=self.queue, body=message, properties=pika.BasicProperties(delivery_mode=2))