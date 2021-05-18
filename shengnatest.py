# coding=utf-8
import pika
import serial
import time
import csv
import configparser
from icecream import ic
import json

cfg_file = 'E:\\shengna\\shengnacfg.ini'

# read .ini according to section
def read_config(r_cfg_file, section):
    #print("Read config from " + os.path.abspath(r_cfg_file))
    config = configparser.ConfigParser()
    config.read(r_cfg_file, encoding='utf-8')
    config_dict = dict(config.items(section))
    # print(config.sections())

    print('\033[1;32m')
    print('{0} = {1}'.format(section, config_dict))
    print('\033[0m')

    return config_dict

myserial = read_config(cfg_file,'serial')
server = read_config(cfg_file,'server')
raspi  = read_config(cfg_file,'raspi')




def wirtedata(value,createTime,sensorId):
    headers = ['value', 'createTime', 'sensorId']
    rows = [
        value,
        createTime,
        sensorId
    ]
    print('write rows to csv',rows)
    dbcsv_dir = raspi['dir']
    with open(dbcsv_dir, 'a+')as f:
        f_csv = csv.writer(f)
        f_csv.writerow(rows)




com = myserial['com']
#com = '/dev/ttyS2'
bsp = myserial['bsp']
#bsp = 9600
#ic(com,bsp)
x = serial.Serial(com, bsp)  # 这是我的串口，测试连接成功，没毛病

nums = 0
num = []
for i in range(10):
    myinput = bytes([0XAA, 0XA0, 0X00, 0X00, 0X00, 0X0A])
    x.write(myinput)
    myout=x.read(17)#读取串口传过来的字节流，这里我根据文档只接收7个字节的数据
    datas =''.join(map(lambda x:('/x' if len(hex(x))>=4 else '/x0')+hex(x)[2:],myout))#将数据转成十六进制的形式
    new_datas = datas.split("/x")#将字符串分割，拼接下标4和5部分的数据
    #ic(new_datas)
    #ic(new_datas[9],new_datas[10],int(hex(int(new_datas[9], 16)), 16),int(hex(int(new_datas[10],16)),16))
    my_need = int(hex(int(new_datas[9], 16)), 16)* 256 + int(hex(int(new_datas[10],16)),16)
    #ic(my_need)
    num.append(my_need)
    nums+=my_need

nums/=10
ic(nums,num)



createTime = int(time.time())
sensorId = raspi['id']



user = server['user']
mm = server['mm']
ip = server['ip']
port = server['port']



try:
    credentials = pika.PlainCredentials(user, mm)  # mq用户名和密码
    # 虚拟队列需要指定参数 virtual_host，如果是默认的可以不填。
    connection = pika.BlockingConnection(pika.ConnectionParameters(host = ip,port = port,virtual_host = '/',credentials = credentials))
    channel=connection.channel()
    # 声明消息队列，消息将在这个队列传递，如不存在，则创建
    result = channel.queue_declare(queue = 'test',durable = True)
    try:
        message = json.dumps({
                                "createTime": createTime,
                                "sensorId": sensorId,
                                "value": nums
                            })
        ic(message)
        channel.basic_publish(exchange = 'test',routing_key = 'test',body = message)
    except Exception as e:
        ic(e)
    connection.close()
except Exception as e:
    ic(e)
    print('\033[1;35mupload failed ,save to csv \033[0m')
    wirtedata(nums, createTime, sensorId)
