from flask import Flask,request,jsonify,Response
from flask_cors import CORS
from openai import OpenAI
import httpx
#mport mysql.connector
import json,time
import sqlite3
app = Flask(__name__)
CORS(app)


def llmapi(chat_msg):
    # 这里假设我们有一个外部 API 的响应，我们将其简化为一个示例字符串
    api_response = "你好，这是一个测试响应。"

    # 创建一个生成器，逐字符地返回 API 的响应
    for char in api_response:
        # 注意这里不使用 json.dumps 或 json.loads，因为我们返回的是原始字符
        yield {'choices': [{'delta': {'content': char}}]}
        time.sleep(0.1)  # 添加延迟，以模拟网络请求的等待时间
def mock_db_query(query_type, params=None):
    if query_type == 'login':
        # 模拟登录成功
        return [("Logged in successfully",)]
    elif query_type == 'register':
        # 检查用户名或电子邮件是否已存在
        existing_users = [
            {'username': 'testuser', 'password': 'testpass', 'email': 'test@test.com'},
            {'username': 'anotheruser', 'password': 'anothertest', 'email': 'another@test.com'}
        ]
        if any(user['username'] == params[0] for user in existing_users):
            return existing_users  # 用户名已存在
        elif any(user['email'] == params[2] for user in existing_users):
            return existing_users  # 邮箱已存在
        else:
            return []  # 注册成功
    elif query_type == 'get_history':
        # 返回模拟的历史记录数据
        return [json.dumps([{"msg": "你好，我怎么帮助你？", "local": False}, {"msg": "我需要项目上的帮助。", "local": True}])]
    elif query_type == 'get_account_info':
        # 返回模拟的账户信息
        return [{"username": "testuser", "email": "test@test.com"}]
    elif query_type == 'delete_account':
        # 删除账户确认
        return []
    elif query_type == 'change_password':
        # 密码更改确认
        return []

conn = sqlite3.connect('my_database.db')

# 创建一个Cursor对象并调用其execute()方法来执行SQL命令
cursor = conn.cursor()

##api
def llmapi(message):

    return json.loads(message)
# print(llmapi('你好'))
#用户登录查询

# 登录模拟
@app.route('/login', methods=['POST'])
def userlogin():
    login_data = request.get_json()
    login_name = login_data['username']
    login_password = login_data['password']
    result = mock_db_query('login')
    if result:
        return jsonify({"code": 200, "message": "登录成功"})
    else:
        return jsonify({"code": 201, "message": "登录失败"})


# 注册模拟
@app.route('/register', methods=['POST'])
def userregister():
    register_data = request.get_json()
    register_name = register_data['username']
    register_password = register_data['password']
    register_email = register_data['email']
    result = mock_db_query('register', (register_name, register_password, register_email))
    if result:
        if any(user['username'] == register_name for user in result):
            return jsonify({"code": 199, "message": "用户已存在"})
        elif any(user['email'] == register_email for user in result):
            return jsonify({"code": 198, "message": "此邮箱已绑定账号"})
    return jsonify({"code": 200, "message": "注册成功"})
    
# ##获取历史记录

# 1.   [["",""],[]]
# [["{}",{}],[{},{}]]
@app.route('/chathistory', methods=['GET'])
def chathistory():
    username = request.args.get('username')
    history_result = mock_db_query('get_history')
    # 将JSON字符串转换为Python对象
    history_result = json.loads(history_result[0])
    return jsonify({"code": 200, "history": history_result})
    

##获取账户信息
# 获取账户信息模拟
@app.route('/accountinfo', methods=['GET'])
def getaccountinfo():
    accountinfo_username = request.args.get('username')
    result = mock_db_query('get_account_info')
    if result:
        return jsonify({"code": 200, "username": result[0]['username'], "email": result[0]['email']})
    else:
        return jsonify({"code": "201"})
# 删除账户模拟
@app.route('/delete_account', methods=['POST'])
def deleteaccount():
    deleteaccount_data = request.get_json()
    deleteaccount_name = deleteaccount_data['username']
    mock_db_query('delete_account')  # 执行删除（模拟）
    return jsonify({"code": 200, "message": "删除成功"})

# 更改密码模拟
@app.route('/change_password', methods=['POST'])
def changepassword():
    basic_data = request.get_json()
    username = basic_data['username']
    old_password = basic_data['oldPassword']
    new_password = basic_data['newPassword']
    result = mock_db_query('change_password')  # 执行密码更改（模拟）
    if result:
        return jsonify({"code": 200, "message": "修改密码成功"})
    else:
        return jsonify({"code": 400, "message": "原密码错误"})

@app.route('/analyze', methods=['POST'])
def analyze_document():
    data = request.get_json(silent=True) or {}
    doc_path = data.get('path')
    temperature = data.get('temperature')
    # 这里为演示返回固定结果，后续可替换为真实分析逻辑
    if not doc_path:
        return jsonify({"code": 400, "message": "缺少参数 path"}), 400
    result_text = f"已接收文档路径: {doc_path}\n分析temperature: {temperature if temperature is not None else '默认'}\n分析结果: 示例结果（请接入真实模型）"
    return jsonify({"code": 200, "result": result_text})

##流式输出对话
@app.route('/chat/chat',methods=['GET'])
def llmchat():
    chat_msg = request.args.get('query')
    chat_username = request.args.get('username')
    print(chat_msg)
    print(chat_username)
    # chat_msg = "你好"  # 示例数据，实际中可以从请求中获取
    chunks = [
        {"choices": [{"delta": {"content": "Hello"}}]},
        {"choices": [{"delta": {"content": " world!"}}]},
        {"choices": [{"delta": {"content": "."}}]},
        {"choices": [{"delta": {}}]},  # 空的delta表示完成
    ]
    #completion = llmapi(chat_msg)  # 假设 llmapi 是你的函数，能返回一个可迭代的chunk
    completion = [
        {
            "choices": [
                {
                    "delta": {
                        "content": "第一条消息"
                    }
                }
            ]
        },
        {
            "choices": [
                {
                    "delta": {
                        "content": "第二条消息"
                    }
                }
            ]
        },
        {
            "choices": [
                {
                    "delta": {
                        "content": None
                    }
                }
            ]
        },
        {
            "choices": [
                {
                    "delta": {
                        "content": "第三条消息"
                    }
                }
            ]
        }
    ]

    def generate():
        for chunk in completion:
            delta = chunk["choices"][0]["delta"]
            if delta["content"] is not None:
                yield f"data: {json.dumps({'message': delta['content']})}\n\n"  # 转换为JSON字符串并添加SSE格式
            time.sleep(0.1)
        yield f"data: {json.dumps({'message': 'done'})}\n\n"  # 最后发送完成信号

    # def generate():
    #     for chunk in completion:
    #         delta = chunk.choices[0].delta
    #         if delta.content is not None:
    #             yield f"data: {json.dumps({'message': delta.content})}\n\n"  # 转换为JSON字符串并添加SSE格式
    #         time.sleep(0.1)
    #     yield f"data: {json.dumps({'message': 'done'})}\n\n"  # 最后发送完成信号

    return Response(generate(), mimetype='text/event-stream')


if __name__ == '__main__':
    app.run(debug=True)

