#!/usr/bin/python
# -*- coding:utf-8 -*-
# author : b1ng0
import time
from threading import RLock
import collections
thread_lock = RLock()
# room=0
sessions= collections.OrderedDict()
sessions_client = collections.OrderedDict()
sessions={}
sessions_client={}
# conns = []
options = {
    'Hash_option': 2,
    'Key_option': 1,
    'Len_Ru': 2,
#    'Zip': 0
}

# 处理全局变量conns
def clear_and_add(data,room):
    with thread_lock:
    # if len(conns) != 0:
    #     del conns[0]
    # conns.append(data)
        conns = []
        conns.append(data)
        sessions_client[room]=conns
    time.sleep(1)

# 处理全局变量sessions
def add_session(key, value):
    sessions[key] = value

def get_sessions():
    return sessions

def del_session(key):
    if sessions.has_key(key):
        sessions.pop(key)
        
def del_dsessions_client (key):
      if sessions_client.has_key(key):
        sessions_client.pop(key)     
# 处理全局变量options
def get_options():
    return options

def set_options(key, value):
    options[key] = value

def change_options(new_options):
    global options
    options = new_options

#对面图像进行解密
def img_decode():
    if os.system(part2dec) == 0:
        if os.system(j2k2png) == 0:
            return 0
    return 1
