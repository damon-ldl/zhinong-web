import request from '../index'
import { baseURL } from '../config/index'; // 引入 baseURL

// 所有的接口API

// 登录请求
export const LoginAPI = (params)=>request.post("/login",params);


// 注册请求
export const RegisterAPI = (params)=>request.post("/register",params);


// 获取历史对话记录
export const ChatHistoryAPI = (params)=>{
    // 构建带参数的URL
    const url = `/chathistory?username=${params.username}`;
    // 发送GET请求
    return request.get(url);
}

// 获取账户信息
export const GetAccountInfoAPI = (params)=>{
    // 构建带参数的URL
    const url = `/accountinfo?username=${params.username}`;
    // 发送GET请求
    return request.get(url);
}

// 删除账户操作
export const DeleteAccountAPI = (params)=>request.post("/delete_account",params);


// 修改密码操作
export const ChangePasswordAPI = (params)=>request.post("/change_password",params);

// 与llm模型对话
// export const ChatLLMAPI = (params)=>request.post("/chat/chat",params);

// 与llm模型对话--流式输出的模式
export const ChatLLMAPI = (params) => {
    return new EventSource(`${baseURL}/chat/chat?query=${params.msg}&username=${params.username}`);
};



