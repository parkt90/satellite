#!/usr/bin/python
# -*- coding:utf-8 -*-
# author : b1ng0
import time
import threading
import copy
import json
import collections
# 奇 
import sys
from Queue import Queue
from flask.globals import g
from pympler import asizeof
socketio_msg_queue = Queue(maxsize=50000)
# m_lock = threading.Lock()
# 设置ip地址
ncc_ip = '127.0.0.1'
user_ip = '127.0.0.1'

# 奇 有序字典 后面考虑会用到
r = threading.RLock()
# t1 = threading.Thread(target=add)
sessions= collections.OrderedDict()
# sessions = {}
sessions = {"123": {"time": 1562827835, "IDu": "ff4b43ede3bfdaa52ea7f97593f8897fd9a41645", "sessionKey": "07b12e43db2ab22e9ba74afda5b29d5c3496495ca49b786b3bfbe180ee896d2f", "Ku": "124640bf2792a0cdce2c04e13326d67bf013bac6ce546616b04888e7c4e68631", "sessionMACKey": "d9186f2e39f03f94946af0ecc4076201ad9dd56552d79bdc42ba3a06209f32d0"}}
tmp=''
conns = []
# flag=1

options = {
    'Hash_option': 2,
    'Key_option': 1,
    'Len_Ru': 2,
    'Zip': 0
}

# 记录接入用户
conn_user = 0
succ_user = 0
# 奇 占用内存
storage=0
num=0
# 处理全局变量conns
def clear_and_add(data):
    if len(conns) != 0:
        del conns[0]
    conns.append(data)
    time.sleep(1)
# qi 测试函数
# 处理全局变量conns
def add():
    r.acquire(0.01)
    # global flag
    # while(flag==0):
    #     time.sleep(0.005)
    #     global flag
    # print data
    data=eval(tmp)
    # socketio_msg_queue.put(data)
    data=json.dumps(eval(tmp))
    conns.append(data)
    r.release()
    # time.sleep(0.1)

def change(data):
    global tmp
    tmp=''
    tmp= data
    # tmp1=json.dumps(tmp)
    # return json.dumps(tmp)
# def remove(conns):
#         r.acquire()
#         # print 1
#         # for i in range(len(conns)):
#         #     conns.pop(0)
#         conns[:]=[]
#         r.release()
        


# 处理全局变量sessions
def add_session(key, value):
    sessions[key] = value

def get_sessions():
    return sessions
# 奇 get sessions 占用内存 bytes
def get_sessions_storage():
    # temp=round(float(asizeof.asizeof(sessions))/(1024*1024),2)
    # global storage
    # storage=storage if  storage>temp else temp

    # 导出存贮容量数据
    # global num
    # num+=1
    # if num % 200==0:
    #     temp_memory=round(float(asizeof.asizeof(sessions))/(1024),2)
    #     with open("data.txt", "a+") as f:
    #         f.write(str(temp_memory)+'\n')
    # print storage;
    # temp=round(float(asizeof.asizeof(sessions.items(-1)))/(1024*1024),2)
    temp_stor=asizeof.asizeof(sessions.items()[-1])
    global storage
    storage+=temp_stor
    storage1=round(float(storage)/(1024*1024),2)
    # storage=storage1 if  storage>temp_stor else temp_stor
    return storage1

def get_sessionkey(key):
    return sessions.get(key)

def del_session(key):
    if sessions.has_key(key):
        sessions.pop(key)
        
# 处理全局变量options
def get_options():
    return options

def set_options(key, value):
    options[key] = value

def change_options(new_options):
    global options
    options = new_options

# 判断timestamp
def is_timeout(timestamp):
    now = int(time.time())
    if now>=int(timestamp) and now-int(timestamp)<=180:
        return False
    return False