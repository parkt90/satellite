# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import *
import json, hashlib, random, time, hmac
import requests
import webbrowser
import os
import threading

from datetime import datetime
from crypty_helper.xor import *
from crypty_helper.AES_use import *
from crypty_helper.DES_use import *
from crypty_helper.DES_3_use import *
from gl import *
from imgCompress import imgCompress

app = Flask(__name__)
CORS(app, supports_credentials=True)

m_lock = threading.Lock()
# socketio = SocketIO(app)
socketio = SocketIO(app, async_mode='threading')

#####################多线程并发设置#######################
maxs=20  ##并发的线程数量
threadLimiter=threading.BoundedSemaphore(maxs)
class ReqAuth(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        threadLimiter.acquire()  #获取 qi 这里相当于把线程加了锁
        try:
            reqAuth()
        except:
            print "Error: unable to start thread"
        finally:
            threadLimiter.release() #释放 这里是把线程锁解开
########################################################

@app.route('/options',methods=['GET','POST'])
def choose():
    if(request.method == "POST"):
        options['Key_option'] = request.form.get('keyOption')
        options['Hash_option'] = request.form.get('hashOption')
        options['Len_Ru'] = request.form.get('RandomOption')
        #print request.data
        print options
        change_options(options)
        #return request.form.get('RandomOption')
    return render_template('list.html')

@app.route('/',methods=['GET','POST'])
def list():
    #return render_template('test.html')
    return render_template('list.html')

@app.route('/authmessage',methods=['GET','POST'])
def index():
    return render_template('display.html')

@socketio.on('client_event')
def client_msg(msg):
    #emit('server_response', {'data': msg['data']})
    while 1:
        global conns
        emit('server_response', {'data': conns})
        time.sleep(0.5)

@app.route('/register',methods=['GET','POST'])
def register():
    url = "http://127.0.0.1:7543/register"
    resp = requests.post(url, data=request.data)
    if(resp.status_code != 500):
         #print datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
         data = json.loads(resp.content)
         print data
         with open("userInfo.json", "w") as userInfo:
             json.dump(data,userInfo)
         return resp.content
    return "fail"

# 用户第一次请求需要的所有数据
@app.route('/reqAuth',methods=['GET','POST'])
def getReqAuthData():
    timestamp = int(time.time())
    # 32
    #Ru = random.randint(10000000000000000000000000000000, 99999999999999999999999999999999)
    # Ru 根据终端配置的随机数长度 生成的随机数
    Ru = getRandom()
    # 读取用户信息
    with open("userInfo.json", "r") as userInfo:
        userInfo = json.load(userInfo)
	#H = '0' flask
    #H = hashlib.sha256(userInfo["userKey"] + str(Ru)).hexdigest()
    # 使用异或运算和哈希函数计算得到的随机数H=r⊕h(K||Ru) 每次认证H都会改变，间接导致PIDu会变
    H = getHash(userInfo["userKey"] + str(Ru))
    #  异或后编码 base64编码算法 将非ASCII字符的数据转换成ASCII字符 适合在http下传输
    H = xor_encrypt(userInfo["preRandom"], H)
    # PIDu=IDu⊕H 用户的临时身份信息
    PIDu = xor_encrypt(str(userInfo["userId"]), H)
    # 消息验证码MACu=h(IDu||Ru||T)
    #MACu = hashlib.sha256(userInfo["userId"] + str(Ru) +str(timestamp)).hexdigest()
    MACu = getHash(userInfo["userId"] + str(Ru) +str(timestamp))
    #ru = hashlib.sha256(userInfo["userKey"] + userInfo['preRandom']).hexdigest()
    #为了保证消息的新鲜性；ru是终端通过生成的随机数Ru和之前注册获得的随机数r共同计算得到的
    # 随机数ru=Ru⊕h(K||r)
    ru = getHash(userInfo["userKey"] + userInfo['preRandom'])
    ru = xor_encrypt(str(Ru), ru)

    return json.dumps(
        {
            "Tu":str(timestamp),     # 时间戳；
            "Hu":H,                # 哈希运算随机数H
            "PIDu":PIDu,            #用户临时身份
            "MACu":MACu,            #用户消息验证码
            "Ru":ru,                # 每次更新后的随机数 异或解码后可以找到NCC与用户共享的随机数r
            "Options":get_options() #用户配置选项
        }
    )

# 用户向卫星发起第一次请求
def reqAuth():
    #print datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    url = "http://127.0.0.1:2333/reqAuth"
    # proxies = {'http': 'http://192.0.2.30:8080'}
    m_lock.acquire()
    data = getReqAuthData()
    # m_lock.release()
    # qi 第一次认证数据 110 行数据 延时和2秒
    # clear_and_add(data)
    # 真正计算开始时间
    # m_lock.acquire()
    startTime = int(round(time.time() * 1000))
    m_lock.release()
    resp = requests.post(url, data=data)
    m_lock.acquire()
    endtime =  int(round(time.time() * 1000))
    authtime = endtime - startTime
    #print datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    # m_lock.acquire()
    ru = json.loads(data)["Ru"]
    data = json.loads(resp.content)
    data['authtime'] = authtime
    
    # to = json.dumps(data)
    # qi卫星返回给用户数据 真正延时和 10+2 S 认证延时6+2 （时间戳以及计算完毕了，不会随睡眠时间增加了.而且返回前数据以及打印出来了，所以显示比运行少2秒）
    # clear_and_add(to)
    if data['ReqAuth'] == "500":
        global num
        num+=1
        print "failed total...",num
        m_lock.release()
        return "0"
    else:
        
        secretHsat = data["secretHsat"]
        secert_sessionId = data["sessionId"]
        MAC = data["MAC"]
        # print MAC
        # 对MAC进行验证
        with open("userInfo.json", "r") as userInfo:
            userInfo = json.load(userInfo)
            # 终端设备计算MACSAT_key=h(IDu||K||ru)
        MAC_key = bytes(getHash(userInfo["userId"] + userInfo["userKey"] + ru))
        msg = "ReqUserSuccess" + secretHsat + secert_sessionId
        myMAC = getHmac(MAC_key,msg)
        
        # print myMAC
        if MAC != myMAC:
            print "failed..."
            m_lock.release()
            return "0"

        # 解开 secretHsat secretSessionId
        with open("userInfo.json", "r") as userInfo:
            userInfo = json.load(userInfo)
        Ku = userInfo["userKey"]
        IDu = userInfo["userId"]
        Ku_use = Ku
        Hsat = decryptData(secretHsat, Ku_use)
        sessionId = decryptData(secert_sessionId, Ku_use)
        # 生成会话密钥 sessionKey sessionMACKey
        sessionKey = getHash(Hsat + Ku)
        sessionMACKey = getHash(IDu + Hsat)

        sessions = {
             "IDu":IDu,
             "Ku":Ku,
             "sessionKey":sessionKey,
             "sessionMACKey":sessionMACKey,
             "time": int(time.time())
        }
        add_session(sessionId, sessions)

        # print sessionId, sessionKey, sessionMACKey
        # qi
        # print "auth success..."
        m_lock.release()
        return "1"

# 用户二次认证请求需要的所有数据
@app.route('/userAuthtwice',methods=['GET','POST'])
def getReqAuthtwiceData():
    sessions = get_sessions()
    print sessions
    # 奇：个人认为有点问题
    sessionId = sessions.keys()[0]
    sessionKey = sessions[sessionId]['sessionKey']
    MACKey = sessions[sessionId]['sessionMACKey']
    timestamp = int(time.time())
    Ru = getRandom()
    # 读取用户信息
    with open("userInfo.json", "r") as userInfo:
        userInfo = json.load(userInfo)
    Ku = userInfo["userKey"]
    Ku_use = Ku
    encode_data = encryptData(userInfo["userId"] + sessionKey + MACKey, Ku_use)
    # MAC_key=h(K||IDu||Ru’)
    MAC_key = getHash(userInfo["userKey"] + userInfo["userId"]  + str(Ru))
    msg = str(encode_data) + str(Ru) + str(timestamp) + sessionId
    MAC = getHmac(MAC_key , msg)

    data = json.dumps({
            "ReqAuth": "second",
            "sessionId":sessionId,
            "Ru":str(Ru),
            "Tu":str(timestamp),
            "encode_data":encode_data,
            "MAC":MAC
        })
    return reqAuthtwice(data,Ru,sessionKey,MACKey)

# 用户向卫星发起二次认证请求
def reqAuthtwice(data,Ru,sessionKey,MACKey):
    # clear_and_add(data)
    startTime = int(time.time()*1000)
    # qi   用户准备好第二次认证数据，发起第二次认证 真正多余延时和 2 S  多余认证延时0
    # sessionId=data["sessionId"]
    #print datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    url = "http://127.0.0.1:2333/secondAuth"
    # proxies = {'http': 'http://192.0.2.30:8080'}
    #startTime = int(time.time()*1000)
    resp = requests.post(url, data=data)
    endtime = int(time.time() *1000)
    authtime = endtime - startTime
    if resp.status_code == 500:
        print "failed..."
        return "0"
    #print datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    data =  json.loads(resp.content)
    data['authtime'] = authtime
    print data
    to = json.dumps(data)

    Rs = data["Rs"]
    Ts = data["Ts"]
    new_sessionId = data["sessionId"]
    MAC = data["MAC"]
    print MAC
    # 对MAC进行验证
    with open("userInfo.json", "r") as userInfo:
        userInfo = json.load(userInfo)
    MAC_key = bytes(getHash(userInfo["userKey"] + userInfo["userId"] + str(Ru)))
    msg =  Rs + Ts + new_sessionId
    myMAC = getHmac(MAC_key,msg)
    print myMAC
    if MAC != myMAC:
        print "failed..."
        return "0"

    # 解开 secretHsat secretSessionId
    with open("userInfo.json", "r") as userInfo:
        userInfo = json.load(userInfo)
    Ku = userInfo["userKey"]
    IDu = userInfo["userId"]
    # Ku_use = Ku
    # Hsat = decryptData(secretHsat, Ku_use)
    # sessionId = decryptData(secert_sessionId, Ku_use)

    # 生成会话密钥 sessionKey sessionMACKey
    sessionKey = getHash(Ku + str(Ru) + Rs + sessionKey)
    sessionMACKey = getHash(IDu + str(Ru) + MACKey)
    # qi 项目报告上面这样写的，个人感觉有点奇怪。可能为下面这种情况。
    # sessionMACKey = getHash(IDu + str(Ru) + Ku+ MACKey)

    sessions = {
         "IDu":IDu,
         "Ku":Ku,
         "sessionKey":sessionKey,
         "sessionMACKey":sessionMACKey,
         "time": int(time.time())
    }
    add_session(new_sessionId, sessions)
    # del_session(sessionId)
    # # qi卫星返回给用户数据 真正延时和 6+2 S  认证延时4（时间戳以及计算完了，不会随睡眠时间增加了.而且返回前数据以及打印出来了，所以显示比运行少2秒）
    # clear_and_add(to)
    print new_sessionId, sessionKey, sessionMACKey
    print "auth success..."
    return "1"

@app.route('/reqwebbrowser',methods=['GET','POST'])
def webbrowseraccess():
    url = "http://127.0.0.1:2333/success"
    sessions = get_sessions()
    print 
    sessions
    try:
        sessionId = sessions.keys()[0]
        data = json.dumps({
            "sessionId": str(sessionId)
        })

        resp = requests.post(url, data=data)
        #return resp.text
        if resp.status_code == 200:
            return render_template('success.html')
        else:
            return render_template('failed.html'), 500
    except Exception, e:
        print e
        return render_template('failed.html'), 500

    #if sessions == ""

@app.route('/picture',methods=['GET','POST'])
def datatransport():
    request_data = json.loads(request.data)
    url = "http://127.0.0.1:2333/reqImg"
    sessions = get_sessions()
    # print sessions
    try:
        sessionId = sessions.keys()[0]
        data = json.dumps({
            "sessionId": str(sessionId),
            "imgId": request_data['imgId'],
            "ratioId": request_data['ratioId']
        })

        resp = requests.post(url, data=data)
        if(resp.status_code == 401):
            return "2"

        #return resp.text
        print resp.text
        imgData = json.loads(resp.text)
        try:
            content = imgData['content']
            sessionId = imgData['sessionId']
            MAC = imgData['MAC']
            img_key = imgData['img_key']

            # 读取sessions
            data = json.loads(authResult())

            mySessionId = data['sessionId']
            MACKey = bytes(data['MACKey'])
            sessionKey = data["sessionKey"]
            #打印出认证后图像加密传输所使用的相关参数信息
            print ("mySessionId:",mySessionId)
            print ("MACKey:",MACKey)
            print ("sessionKey:",sessionKey)

            # 验证 MAC
            myMAC = getHmac(MACKey, content)
            if MAC == myMAC:
               key_use = sessionKey

               resp = decryptData(content, key_use)
               img_key = decryptData(img_key, key_use)
               # with open("static/sate.png", "wb") as img:
               #     img.write(resp)
               with open("imgCompress/transcoding/transcoding/Client/part.j2k", "wb") as img:
                   img.write(resp)
               with open("imgCompress/transcoding/transcoding/Client/lena.key", "wb") as img:
                   img.write(img_key)
               imgCompress.img_decode()
               return "1"

            return "0"
        except Exception, e:
           print e
           return "0"
    except Exception, e:
       print e
       print "ddddddddddddddddddddd"
       return "0"

def authResult(sessionId):
    sessions = get_sessions()
    return {
        "sessionId":sessionId,
        "sessionKey":sessions[sessionId]["sessionKey"],
        "MACKey":sessions[sessionId]["sessionMACKey"],
        "IDu":sessions[sessionId]["IDu"],
        "Ku":sessions[sessionId]["Ku"],
    }
# 处理options['Len_Ru']
def getRandom():
    options = get_options()
    if options['Len_Ru'] == 1: # 16 duan
        return random.randint(1000000000000000, 9999999999999999)
    elif options['Len_Ru'] == 2: # 32 jiaochang
        return random.randint(10000000000000000000000000000000, 99999999999999999999999999999999)
    elif options['Len_Ru'] == 3: # 48 chang
        return random.randint(100000000000000000000000000000000000000000000000, 999999999999999999999999999999999999999999999999)

# 处理options['Hash_option']
def getHash(msg):
    options = get_options()
    if options['Hash_option'] == 1: # sha1
        return hashlib.sha1(msg).hexdigest()
    elif options['Hash_option'] == 2: # sha256
        return hashlib.sha256(msg).hexdigest()
    elif options['Hash_option'] == 3: # sha512
        return hashlib.sha512(msg).hexdigest()

#.................................................................................................................................#
# 处理hmac
def getHmac(MAC_key, msg):
    options = get_options()
    if options['Hash_option'] == 1: # sha1
        return hmac.new(MAC_key, msg, hashlib.sha1).hexdigest()
    elif options['Hash_option'] == 2: # sha256
        return hmac.new(MAC_key, msg, hashlib.sha256).hexdigest()
    elif options['Hash_option'] == 3: # sha512
        return hmac.new(MAC_key, msg, hashlib.sha512).hexdigest()

# 处理options['Key_option']
def encryptData(data, key):
    options = get_options()
    if options['Key_option'] == 1: # AES
        return aes_encrypt(data, key)
    elif options['Key_option'] == 2: # DES
        return des_encrypt(data, key)
    elif options['Key_option'] == 3: # 3DES
        return three_des_encrypt(data, key)

def decryptData(data, key):
    options = get_options()
    if options['Key_option'] == 1: # AES
        return aes_decrypt(data, key)
    elif options['Key_option'] == 2: # DES
        return des_decrypt(data, key)
    elif options['Key_option'] == 3: # 3DES
        return three_des_decrypt(data, key)
#.........................................................................................................................................#

# 认证结果展示
def authResult():
   sessionId = sessions.keys()[0]
   return json.dumps({
       "sessionId":sessionId,
       "sessionKey":sessions[sessionId]["sessionKey"],
       "MACKey":sessions[sessionId]["sessionMACKey"]
   })

@app.route('/userAuth', methods=['GET','POST'])
@cross_origin()
def userAuth():
    status = reqAuth()
    return status

@app.route('/userAuthtwice', methods=['GET','POST'])
@cross_origin()
def userAuthtwice():
    status = reqAuth()
    return status

if __name__ == '__main__':
    reqAuth()
###############测试并发线程性能##############
    for i in range(200):
        cur=ReqAuth()
        cur.start()
    # for i in range(50):
        # cur.join()
###########################################
    socketio.run(
            app,
            host='0.0.0.0',#任何ip都可以访问
            # host='::',
            port=9000,#端口
            # debug=True
            )
    # while 1:
    #    reqAuth()
    #    time.sleep(3)
       
