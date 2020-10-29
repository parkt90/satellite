#!/usr/bin/python
# -*- coding:utf-8 -*-
# author : b1ng0
import time
num=0
sessions = {}
conns = []
options = {
    'Hash_option': 2,
    'Key_option': 1,
    'Len_Ru': 2,
#    'Zip': 0
}

# 处理全局变量conns
def clear_and_add(data):
    if len(conns) != 0:
        del conns[0]
    conns.append(data)
    time.sleep(0.75)

# 处理全局变量sessions
def add_session(key, value):
    sessions[key] = value

def get_sessions():
    return sessions

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

#对面图像进行解密
def img_decode():
    if os.system(part2dec) == 0:
        if os.system(j2k2png) == 0:
            return 0
    return 1
