from flask import Flask,request,jsonify,Response
from flask_cors import CORS
from openai import OpenAI
import httpx
import mysql.connector
import json,time
app = Flask(__name__)
CORS(app)   
db = mysql.connector.connect(
    host="",
    user="",
    password="",
    database="",
    buffered = True
)
cursor = db.cursor()


##api
def llmapi(message):
    pass
# print(llmapi('你好'))
#用户登录查询

@app.route('/login', methods=['POST'])
def userlogin():
    login_data = request.get_json()    #data ={"username":"","password":""}
    login_name = login_data['username']
    login_password = login_data['password']
    user_info_pre = (f"{login_name}",f"{login_password}")
    cursor.execute("SELECT * FROM user_info WHERE user_name=%s AND user_password=%s",user_info_pre)
    result = cursor.fetchall()
    if result != []:
        return jsonify({"code":200,"message":"successful"})
    else:
        return jsonify({"code":201,"message":"failed"})

# ##用户注册
@app.route('/register',methods=['POST'])
def userregister():
    register_data = request.get_json()
    # print(register_data)
    register_name = register_data['username']
    register_password = register_data['password']
    register_email = register_data['email']
    user_info_pre_register = (f"{register_name}",f"{register_password}",f"{register_email}")
    cursor.execute("SELECT * FROM user_info WHERE user_name=%s",(f"{register_name}",))
    name_result = cursor.fetchall()
    cursor.execute("SELECT * FROM user_info WHERE user_email=%s",(f"{register_email}",))
    email_result = cursor.fetchall()
    if name_result != []:
        return jsonify({"code":199,"message":"用户已存在"})
    elif email_result != []:
        return jsonify({"code":198,"message":"此邮箱已绑定账号"})
    else:
        cursor.execute("INSERT INTO user_info (user_name,user_password,user_email) VALUES (%s,%s,%s)",user_info_pre_register)
        db.commit()
        return jsonify({"code":200,"message":"注册成功"})   
    
# ##获取历史记录

# 1.   [["",""],[]]
# [["{}",{}],[{},{}]]
@app.route('/chathistory',methods=['GET'])
def chathistory():
    username = request.args.get('username')
    cursor.execute("SELECT user_info.user_history FROM user_info WHERE user_name=%s",(username,))
    history_result = cursor.fetchall()
    history_result = json.loads(history_result[0][0])
    # print(history_result)
    for item in history_result:
        list1=[]
        list2=[]
        # print(item)
        # item = json.loads(item)
        for i,sub_item in enumerate(item):
            
            sub_item = json.loads(sub_item)
            if i%2 == 0:
                new_dict = {"id":1,"msg":sub_item['msg'],"local":True}
                list2.append(new_dict)
            else:
                new_dict = {"id":1,"msg":sub_item['msg'],"local":False}
                list2.append(new_dict)
        list1.append(list2)
        # print(list1)
    return jsonify({"code":200,"history":list1})
    

##获取账户信息
@app.route('/accountinfo',methods=['GET'])
def getaccountinfo():
    accountinfo_username = request.args.get('username')
    # print(accountinfo_username)
    # accountinfo_username=accountinfo_data['username']
    cursor.execute("SELECT * FROM user_info WHERE user_name=%s",(accountinfo_username,))
    pre_result = cursor.fetchall()
    if pre_result !=[]:
        username = pre_result[0][1]
        useremail = pre_result[0][3]
        return jsonify({"code":200,"username":f"{username}","email":f"{useremail}"})
    else :
        return jsonify({"code":"201"})

##删除账户信息
@app.route('/delete_account',methods=['POST'])
def deleteaccount():
    deleteaccount_data = request.get_json()
    deleteaccount_name = deleteaccount_data['username']
    cursor.execute("DELETE FROM user_info WHERE user_name=%s",(deleteaccount_name,))
    db.commit()
    return jsonify({"code":200,"message":"删除成功"})

##更改密码
@app.route('/change_password',methods=['POST'])
def changepassword():
    basic_data = request.get_json()
    username = basic_data['username']
    old_password = basic_data['oldPassword']
    new_password = basic_data['newPassword']
    cursor.execute("SELECT * FROM user_info WHERE user_name=%s",(username,))
    result1 = cursor.fetchall()
    if old_password == result1[0][2]:
        cursor.execute("UPDATE user_info SET user_password=%s WHERE user_name=%s",(new_password,username),)
        db.commit()
        return jsonify({"code":200,"message":"修改密码成功"})
    else:
        return jsonify({"code":400,"message":"原密码错误"})


##流式输出对话
@app.route('/chat/chat',methods=['GET'])
def llmchat():
    chat_msg = request.args.get('query')
    print(chat_msg)
    # chat_msg = "你好"  # 示例数据，实际中可以从请求中获取
    completion = llmapi(chat_msg)  # 假设 llmapi 是你的函数，能返回一个可迭代的chunk
    
    def generate():
        for chunk in completion:
            delta = chunk.choices[0].delta
            if delta.content is not None:
                yield f"data: {json.dumps({'message': delta.content})}\n\n"  # 转换为JSON字符串并添加SSE格式
            time.sleep(0.1)
        yield f"data: {json.dumps({'message': 'done'})}\n\n"  # 最后发送完成信号

    return Response(generate(), mimetype='text/event-stream')


if __name__ == '__main__':
    app.run(debug=True)

