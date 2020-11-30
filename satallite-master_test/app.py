# -*- coding:utf-8 -*-
# from threading import Event
import eventlet
eventlet.monkey_patch()
from flask import Flask, jsonify, request, render_template, Response, send_from_directory, abort
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import json
import webbrowser
# import queue

from threading import RLock




from dealRequest import *
from gl import *
from imgCompress import imgCompress
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app, supports_credentials=True)

thread_lock = RLock()
thread = None

# socketio = SocketIO(app)
socketio = SocketIO(app,async_mode='eventlet')
with open("log.txt", "r+") as f:
            f.truncate()

@app.route('/')
def index():
    # return app.send_static_file('show.html')
    return app.send_static_file('display/index.html')

@app.route('/show')
def show():
    return app.send_static_file('show.html')


# @socketio.on('client_event')
# def client_msg(msg):
#     # emit('server_response', {'data': msg['data']})
#     while 1:
#         try:
#             socketio.emit('server_response', {'data':data_temp})
#             t2=threading.Thread(target=remove,kwargs={"conns": conns, "data_temp": data_temp})
#             t2.start()
#             t2.join()
            
#             # time.sleep(0.1)
#             eventlet.sleep(0.9)
#         except:
#             print "Error: unable to start thread t2"
        
        # t2.join()
        # if len(conns):
        #     # global flag
        #     # flag==0
        #     # time.sleep(0.001)
        #     # data=[]
        # # global conns
        #     # data=[]
        #     data=copy.deepcopy(conns)
        #     emit('server_response', {'data': data})
        #     for i in range(len(data)):
        #         # global conns
        #         # if  bool(1-bool(conns)): 
        #         conns.pop(0)
        # # flag==1
        # time.sleep(0.5)
        # eventlet.sleep(0.2)
# def remove(conns,data_temp):
#         r.acquire()
#         data_temp[:]=[]
#         for i in conns:
#             data_temp.append(i) 
#         # socketio.emit('server_response', {'data':data_temp})
#         conns[:]=[]
#         r.release()

        # time.sleep(0.5)
        # socketio.sleep(0.5)
@socketio.on('connect', namespace='/test_conn')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)

def background_thread():
    eventlet.spawn_n(gtask_socketio_emit)

def gtask_socketio_emit():
    while True:
        with thread_lock:
            socketio.emit('server_response', {'data': conns},namespace='/test_conn') 
            conns[:]=[]
        eventlet.sleep(2)
        # eventlet.sleep(0.3)
        # while(socketio_msg_queue.qsize>0):
        #  msg = socketio_msg_queue.get()
        #  socketio.emit('server_response', {'data':json.dumps(msg)},namespace='/test_conn')
# while True:
    #     with thread_lock:
    #         socketio.emit('server_response', {'data': conns},namespace='/test_conn') 
    #         conns[:]=[]
    #         eventlet.sleep(0.1)

 

# 用户请求卫星图片
@app.route('/reqImg', methods=['GET', 'POST'])
def reqImg():
    if(request.data):
        request_data = json.loads(request.data)
        sessionId = request_data["sessionId"]

        imgId = request_data["imgId"] # 图片1/2/3
        ratioId = request_data['ratioId'] # 分辨率 1/2/3 低/中/高


        sessions = get_sessions()
        try:
            session_data = sessions[sessionId]
            # 判断session是否过期
            now = int(time.time())
            if now-session_data['time'] > 60*30:
                return "expire", 401

            IDu = session_data['IDu']
            userData = json.dumps({
                'IDu': IDu,
                'sessionId': sessionId,
                'ReqAuth': 'reqImg',
                'ratioId': ratioId,
                'imgId': imgId
            })
            clear_and_add(userData)
        except KeyError:
            return 'you not auth success', 500
         # encode img
        if imgCompress.img_encode(imgId,ratioId) == 1:
            return 'img encode error', 500
        # part.j2k lena.key ==> user
        with open("imgCompress/transcoding/transcoding/Client/part.j2k", "rb") as img:
            img_content = img.read()
        with open("imgCompress/transcoding/transcoding/Client/lena.key", "rb") as key:
            img_key = key.read()
        # 对图像信息进行加密
        if img_content and img_key:
            try:
                data = authResult(sessionId)
                return imgRepo(data, img_content,img_key, imgId)
            except Exception, e:
                print e
                imgError = json.dumps({
                    'error': e,
                    'ReqAuth': 'imgError',
                    'IDu': IDu
                })
                clear_and_add(imgError)
                return "img crypty error", 500

    return "method error", 500
# @app.route('/reqImg', methods=['GET', 'POST'])
# def reqImg():
#     if(request.data):
#         sessionId = json.loads(request.data)["sessionId"]
#         sessions = get_sessions()
#         try:
#             session_data = sessions[sessionId]
#             # 判断session是否过期
#             now = int(time.time())
#             if now-session_data['time'] > 60*30:
#                 return "expire", 401

#             IDu = session_data['IDu']
#             userData = json.dumps({
#                 'IDu': IDu,
#                 'sessionId': sessionId,
#                 'ReqAuth': 'reqImg'
#             })
#             clear_and_add(userData)
#         except KeyError:
#             return 'you not auth success', 500
        
#         with open("static/img/sate.png", "rb") as img:
#             img_content = img.read()
#         # 对图像信息进行加密
#         if img_content:
#             try:
#                 data = authResult(sessionId)
#                 return imgRepo(data, img_content)
#             except Exception, e:
#                 print e
#                 imgError = json.dumps({
#                     'error': e,
#                     'ReqAuth': 'imgError',
#                     'IDu': IDu
#                 })
#                 clear_and_add(imgError)
#                 return "img crypty error", 500

#     return "method error", 500

# 认证成功访问页面
@app.route('/success', methods=['GET', 'POST'])
def success():
    # if request.method == 'POST':
    if(request.data):
        try:
            sessionId = json.loads(request.data)["sessionId"]
            temp_sessions = get_sessions()
            # session_data = temp_sessions[sessionId]
            session_data = temp_sessions.get(sessionId)
            # 判断session是否过期
            now = int(time.time())
            if now-session_data['time'] < 60*30:
                return '200'
            # qi
            # else:  
            #     del_session(sessionId)

            return "expire", 401
        except Exception, e:
            print e
            return "500", 500

    return "500", 500



# 卫星收到用户发来的认证信息，连同自己的认证信息一起发给ncc
@app.route('/reqAuth', methods=['GET', 'POST'])
def reqAuthFromUser():
    startTime = int(time.time()*1000)
    # m_lock.acquire()
    # 这里要对用户信息做出判断
    if(request.data):
        userData = json.loads(request.data)
        # 粗糙的验证用户信息
        if not user_valid(userData):
            return 'timeout', 500
        # 统计接入用户
        
        global conn_user
        global succ_user
        # 奇 
        global storage
        conn_user += 1
        # userData['conn_user'] = conn_user
        # userData['succ_user'] = succ_user
        # change(str(userData))
        temp_data={
            "conn_user":conn_user,
            "succ_user": succ_user,
            "MACu": userData['MACu'],
            "PIDu":userData['PIDu'],
            "Options":userData['Options'] 
        }
        change(str(temp_data))
        # change(userData)
        #  qi增加占用内存信息
        # get_sessions_storage()
        # userData['storage'] = get_sessions_storage() 
        # qi 卫星收到用户数据，并做初步判断 真正延时和 2+2 S 认证延时2
        # 暂时不用 clear_and_add(json.dumps(userData))
        try:
           t1 =threading.Thread(target=add)
           t1.start()
           t1.join()
        except:
            print "Error: unable to start thread t1"
        
        # add(json.dumps(userData))
        # m_lock.release()
        # time.sleep(1)
        # conns.clear
        # m_lock.acquire()
        # 处理认证选项
        # qi 处理多线程时可能需要在这部分加锁
        try:
            new_options = userData['Options']
            # new_options = {
            #     'Hash_option': 1,
            #     'Key_option': 1,
            #     'Len_Ru': 2,
            #     'Zip': 0
            # }
        except Exception, e:
            print "no options from user"
            pass
        else:
            change_options(new_options)
        # 获取卫星认证数据
        # print get_options()
       
        satalliteData = getReqAuthData()
        satalliteData = json.loads(satalliteData)
        # m_lock.release()

        # sendToNcc
        try:
            # sendToNcc会延时4S
            data = sendToNcc(satalliteData, userData)
            # 统计成功信息
            # m_lock.acquire()
            succ_user += 1
            # data['conn_user'] = conn_user
            # data['succ_user'] = succ_user
            # data['storage'] = get_sessions_storage()
            # data = json.dumps(data)
            #  qi 卫星收到用户数据，并做初步判断 真正延时和 8+2 S  认证延时6+2
            # clear_and_add(data)
            
            temp_data1={
                "conn_user":conn_user,
                "succ_user": succ_user,
                "storage":get_sessions_storage(),
                "PIDu":data['PIDu'],
                "ReqAuth":data['ReqAuth'],
                "认证时间" : str(int(round(time.time() * 1000))-startTime)+"ms"

            }
            change(str(temp_data1))
            t3 =threading.Thread(target=add)
            t3.start()
            t3.join()
            # add(data)
            # m_lock.release()
            # time.sleep(1)
            # conns.clear
            # m_lock.acquire()
            return data
        except Exception, e:
            print e
            # m_lock.acquire()
            # data = json.dumps({
            #     "ReqAuth":"500",
            #     "PIDu":userData["PIDu"],
            #     "conn_user": conn_user,
            #     "succ_user": succ_user,
            #     "storage" :get_sessions_storage()
            #     })
            data = json.dumps({
                "ReqAuth":"500",
                "PIDu":userData["PIDu"],
                "conn_user": conn_user,
                "succ_user": succ_user,
                "storage" :get_sessions_storage(),
                "认证时间" : str(int(round(time.time() * 1000))-startTime)+"ms"
            })
            # clear_and_add(data)
            change(str(data))
            t6 =threading.Thread(target=add)
            t6.start()
            t6.join()
            # m_lock.release()
            # time.sleep(1)
            # m_lock.acquire()
            return Response(status=500, response=data)
    else:
        # m_lock.acquire()
        return Response(status=500)

# 二次认证
@app.route('/secondAuth', methods=['GET', 'POST'])
def secondAuth():
    # 接收认证数据
    if request.data:
        try:
            data = json.loads(request.data)
            # dealSecondAuth 休眠4秒时间
            return dealSecondAuth(data)
        except Exception, e:
            print e
            data = json.dumps({
                "RepAuth":"500",
                })
            clear_and_add(data)
            return 'auth error', 500
    else:
        return 'method error', 500

@app.route('/getUserList', methods=['GET', 'POST'])
def getUserList():
    temp_sessions = get_sessions()
    return json.dumps(temp_sessions)


if __name__ == "__main__":
    # webbrowser.open("http://127.0.0.1:2333")
    # CORS(app, supports_credentials=True)
    socketio.run(
        app,
        debug=True,
        host='127.0.0.1',
        port=2333,

        )