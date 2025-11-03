// 全局变量管理，将存储消息的数组
const storedmsg = JSON.parse(sessionStorage.getItem('msgArr'));
const initialmsg = storedmsg ? storedmsg : [];

// 全局变量管理，将存储消息的数组
const storedmsghistory = JSON.parse(sessionStorage.getItem('history'));
const initialmsghistory = storedmsghistory ? storedmsghistory : [];

// 登录标志位
const storedFlag = sessionStorage.getItem('loginFlag');
const initialFlag = storedFlag ? storedFlag : false;

// 用户名称
const userName = sessionStorage.getItem('username');
const initialuserName = userName ? userName : "";


const initstate = {
    msgArr: initialmsg, // 存储消息的数组
    loginFlag: initialFlag, // 登录标志位
    history: initialmsghistory,
    userName: initialuserName, // 用户名称
    ModalOpen: false, // 设置弹窗是否打开
    historyTalk:[]  // 历史聊天记录
}
const reducer = (state=initstate,action) =>{
    switch (action.type) {
        case 'AddMsg':
          return {
            ...state,
            msgArr:[...state.msgArr,action.payload]
          };
        case 'ReduceMsg':
          return {
            ...state,
            msgArr:action.payload
        };
        case 'AddHistory':
          return {
            ...state,
            history:[...state.history,action.payload]
          };  
        case 'ClearMsg':
          return{
            ...state,
            msgArr:[],
            history:[],
          }
        case 'AddRound':
          return{
           ...state,
           round: state.round + 1
          }
        case 'ReduceRound':
          if (state.round > 0) {
            return {
              ...state,
              round: state.round - 1
            };
          } else {
            return {
              ...state,
              round: 0
            };
          } 
        case 'set_loginFlag':
          return{
            ...state,
            loginFlag: action.payload
          }
        case 'set_username':
          return{
            ...state,
            userName: action.payload
          }
          case 'SetMsg':
            return{
              ...state,
              msgArr:action.payload,
            }
          case 'SET_MODALOPEN':
            return{
              ...state,
              ModalOpen: action.payload
            }
          case 'ClearTalk':
            return{
              ...state,
              msgArr:[],
              history:[],
              historyTalk:[],
            }  
        default:
          return state;
    }
}

export default reducer