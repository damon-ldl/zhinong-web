import React,{ useState,useEffect,useRef} from 'react'
import { RightOutlined } from '@ant-design/icons'
import '../../assets/styles/talk.scss'
import local from '../../assets/image/local.png';
import user from '../../assets/image/user.png';
import { useSelector, useDispatch } from 'react-redux';
import { ChatLLMAPI} from '../../request/api/index'
import Send from '../../assets/image/send.png'
import Voice from '../../assets/image/voice.png'
import Link from '../../assets/image/link.png'
import LinkHover from '../../assets/image/linkhover.png'
import Horn from '../../assets/image/horn.png'
// 引入针对回复消息所做的操作图片
import Support from '../../assets/image/support.png'
import Stomp from '../../assets/image/stomp.png'
import Share from '../../assets/image/share.png'
import Copy from '../../assets/image/copy.png'
import Return from '../../assets/image/return.png'
import Key from '../../assets/image/key.png'
import HornHover from '../../assets/image/hornHover.png'
import CopySuccess from '../../assets/image/copysuccess.png'
import ReturnHover from '../../assets/image/returnhover.png'
import CopyHover from '../../assets/image/copyhover.png'
import ShareHover from '../../assets/image/sharehover.png'
import StompHover from '../../assets/image/stomphover.png'
import SupportHover from '../../assets/image/supporthover.png'

function ChatMsg({ index, isLastSystemMsg,onShare,setCurrentStreamingMsg}) {
  const msgArr = useSelector(state => state.msgArr); // 聊天界面显示的所有信息
  const dispatch = useDispatch();
  const [isHovered, setIsHovered] = useState(false);
  const [isHornHovered, setIsHornHovered] = useState(false);
  const [isCopied, setIsCopied] = useState(false); // 新增：复制状态
  const [isReturnHovered, setIsReturnHovered] = useState(false); // Return 图片悬停状态
  const [isCopyHovered, setIsCopyHovered] = useState(false); // Copy 图片悬停状态
  const [isShareHovered, setIsShareHovered] = useState(false); // Share 图片悬停状态
  const [isStompHovered, setIsStompHovered] = useState(false); // stomop 图片悬停状态
  const [isSupportHovered, setIsSupportHovered] = useState(false); // support 图片悬停状态omop 图片悬停状态
  const [loading, setLoading] = useState(false);
  const userName = useSelector(state => state.userName);

  const initialRender = useRef(true);

  useEffect(() => {
    if (initialRender.current) {
      initialRender.current = false;
      return;
    }
    setIsHovered(isLastSystemMsg);
  }, [isLastSystemMsg]);


  const handleCopy = (msg) => {
    navigator.clipboard.writeText(msg).then(() => {
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 1000); // 2秒后恢复原状
    });
  };

  const handleReturnClick = () => {
    const indexToRemoveFrom = msgArr.findIndex(msg => msg.id === index.id);
    const newMsgArr = msgArr.slice(0, indexToRemoveFrom);
    dispatch({ type: 'SetMsg', payload: newMsgArr });
  
    if (indexToRemoveFrom > 0) {
      const previousMsg = msgArr[indexToRemoveFrom - 1];
      const msglocal = {
        id: new Date().getTime(),
        msg: previousMsg.msg,
        local: true
      };
      // 调用后端接口
    setLoading(true);
    const eventSource = ChatLLMAPI(msglocal);

    let accumulatedMsg = '';
    setCurrentStreamingMsg({ id: new Date().getTime(), msg: '', local: false, alertMsg: [] }); // 初始化流式消息

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.message === 'done') {
        eventSource.close();
        setLoading(false);
        setCurrentStreamingMsg(null); // 清除临时消息
        if (accumulatedMsg) {
          const msg = {
            id: new Date().getTime(),
            msg: accumulatedMsg,
            local: false,
            alertMsg: data.docs || [],
          };
          dispatch({ type: 'AddMsg', payload: msg }); // 更新消息数组
        }
      } else {
        accumulatedMsg += data.message;
        const updatedMsg = {
          id: new Date().getTime(),
          msg: accumulatedMsg,
          local: false,
          alertMsg: data.docs || [],
        };
        setCurrentStreamingMsg(updatedMsg); // 更新临时消息
      }
    };

    eventSource.onerror = (error) => {
      console.error('EventSource failed:', error);
      eventSource.close();
      setLoading(false);
      setCurrentStreamingMsg(null); // 清除临时消息
    };
    }
  };
  

  const handleAlertClick = (alertMsg) => {
    const msglocal = {
      id: new Date().getTime(),
      msg: alertMsg,
      local: true
    };
    dispatch({ type: 'AddMsg', payload: msglocal }); // 更新消息数组
    // 调用后端接口
    setLoading(true);
    const eventSource = ChatLLMAPI(msglocal);

    let accumulatedMsg = '';
    setCurrentStreamingMsg({ id: new Date().getTime(), msg: '', local: false, alertMsg: [] }); // 初始化流式消息

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.message === 'done') {
        eventSource.close();
        setLoading(false);
        setCurrentStreamingMsg(null); // 清除临时消息
        if (accumulatedMsg) {
          const msg = {
            id: new Date().getTime(),
            msg: accumulatedMsg,
            local: false,
            alertMsg: data.docs || [],
          };
          dispatch({ type: 'AddMsg', payload: msg }); // 更新消息数组
        }
      } else {
        accumulatedMsg += data.message;
        const updatedMsg = {
          id: new Date().getTime(),
          msg: accumulatedMsg,
          local: false,
          alertMsg: data.docs || [],
        };
        setCurrentStreamingMsg(updatedMsg); // 更新临时消息
      }
    };

    eventSource.onerror = (error) => {
      console.error('EventSource failed:', error);
      eventSource.close();
      setLoading(false);
      setCurrentStreamingMsg(null); // 清除临时消息
    };
  };


  return (
    <div
      className={`msgLine ${index.local ? 'msg-right' : 'msg-left'}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="msg">
        {index.local ? (
          <>
            <img
              className="horn-icon left"
              src={isHornHovered ? HornHover : Horn}
              alt="horn"
              onMouseEnter={() => setIsHornHovered(true)}
              onMouseLeave={() => setIsHornHovered(false)}
            />
            <img className="message-image right" src={user} alt="user" />
          </>
        ) : (
          <>
            <img className="message-image left" src={local} alt="local" />
            <img
              className="horn-icon right"
              src={isHornHovered ? HornHover : Horn}
              alt="horn"
              onMouseEnter={() => setIsHornHovered(true)}
              onMouseLeave={() => setIsHornHovered(false)}
            />
          </>
        )}
        <div className={`${index.local ? 'fr' : 'fl'} ${!index.local && index.msg.trim() !== '' && 'msg-background'}`}>
          {index.msg}
        </div>
        {!index.local && (isHovered || (isLastSystemMsg && index === msgArr[msgArr.length - 1])) &&(
          <div className="system-icons">
            <img src={isSupportHovered?SupportHover:Support} alt="Support"
                onMouseEnter={() => setIsSupportHovered(true)}
                onMouseLeave={() => setIsSupportHovered(false)} />
            <img src={isStompHovered ? StompHover:Stomp} alt="Stomp" 
            onMouseEnter={() => setIsStompHovered(true)}
            onMouseLeave={() => setIsStompHovered(false)}/>
            <img
              src={ isReturnHovered ? ReturnHover : Return} // 根据悬停状态切换图片
              alt="Return"
              onMouseEnter={() => setIsReturnHovered(true)}
              onMouseLeave={() => setIsReturnHovered(false)}
              onClick={handleReturnClick} // 点击事件
            />
            <img
              src={isCopied ? CopySuccess : (isCopyHovered ? CopyHover : Copy)} // 判断是否悬停，并根据条件选择图片
              alt="Copy"
              onMouseEnter={() => setIsCopyHovered(true)}
              onMouseLeave={() => setIsCopyHovered(false)}
              onClick={() => handleCopy(index.msg)} // 点击复制消息
            />
            <img src={ isShareHovered ? ShareHover:Share} 
            onMouseEnter={() => setIsShareHovered(true)}
            onMouseLeave={() => setIsShareHovered(false)}
            alt="Share" onClick={onShare}  />
          </div>
        )}
      </div>
      <div>
        {!index.local && isLastSystemMsg && index.alertMsg && (
          <div className="alert-messages">
            {index.alertMsg.slice(0, 3).map((alert, idx) => (
              <div key={idx} className="alert-message" onClick={() => handleAlertClick(alert)}>
                {alert}
                <RightOutlined className="right-outlined" style={{marginLeft: '10px'}} />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}


console.log('333')
const Talk = () =>  {
  const [text, setText] = useState('');  // 输入框的内容
  const [isLinkHovered, setIsLinkHovered] = useState(false);  // 悬停状态
  const [isRecording, setIsRecording] = useState(false);
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const msgArr = useSelector(state => state.msgArr); // 聊天界面显示的所有信息
  const history = useSelector(state => state.history);
  const chatContainerRef = useRef(null); // 聊天容器的引用
  const [isShareCopied, setIsShareCopied] = useState(false); // 分享复制状态
  const [currentStreamingMsg, setCurrentStreamingMsg] = useState(null); // 新增：当前流式消息
  const userName = useSelector(state => state.userName)
  const updateMsg = (msg) =>{
    dispatch({ type: 'AddMsg', payload: msg });
  }

  const updateMsghistory = (msg) =>{
    dispatch({ type: 'AddHistory', payload: msg });
  }

  const updateRound = () =>{
    dispatch({ type: 'AddRound' });
  }

  const sendMassage= () => {
    if (text.trim() === '') {
      return;
    }
    console.log(text)
    const msglocal = {
      id: new Date().getTime(),
      username: userName  ,
      msg: text ,
      local: true
    };
    console.log('123',userName);
    updateMsg(msglocal); // 更新消息数组
    setText(''); // 清空输入框

    const historyFormatted = history.map(messages => {
      return messages.map(msg => ({
        "role": msg.local ? 'user' : 'assistant',
        "content": msg.msg
      }));
    });
    
    // 转换消息数组格式，准备发送给后端
    const historydata = msgArr.map(msg => ({
        "role": msg.local ? 'user' : 'assistant',
        "content": msg.msg
      }));  
    // 调用后端接口
    setLoading(true);
    const eventSource = ChatLLMAPI(msglocal);

    let accumulatedMsg = '';
    setCurrentStreamingMsg({ id: new Date().getTime(), msg: '', local: false, alertMsg: [] }); // 初始化流式消息

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.message === 'done') {
        eventSource.close();
        setLoading(false);
        setCurrentStreamingMsg(null); // 清除临时消息
        if (accumulatedMsg) {
          const msg = {
            id: new Date().getTime(),
            msg: accumulatedMsg,
            local: false,
            alertMsg: data.docs || [],
          };
          updateMsg(msg); // 更新消息数组
        }
      } else {
        accumulatedMsg += data.message;
        const updatedMsg = {
          id: new Date().getTime(),
          msg: accumulatedMsg,
          local: false,
          alertMsg: data.docs || [],
        };
        setCurrentStreamingMsg(updatedMsg); // 更新临时消息
      }
    };

    eventSource.onerror = (error) => {
      console.error('EventSource failed:', error);
      eventSource.close();
      setLoading(false);
      setCurrentStreamingMsg(null); // 清除临时消息
    };
    
  }
  const handleKeyDown = (e) => {
    if (!isRecording) {
      if (e.keyCode == 13 && e.shiftKey) {
        setText(text + '\n');
        e.target.style.lineHeight = '10px'; // 设置较小的行高
      } else if (e.keyCode == 13) {
        // 阻止原生的换行事件
        e.preventDefault();
        sendMassage();
        // 重置行高样式
        e.target.style.lineHeight = '20px';
      }
    }
  };
  
  const handleInputChange = (e) => {
    if (!isRecording) {
      setText(e.target.value);
      // 如果文本框不为空，则保持较小的行高样式
      if (e.target.value === '') {
        e.target.style.lineHeight = '20px';
      }
    }
  };

  const handleShareClick = () => {
    navigator.clipboard.writeText(window.location.href).then(() => {
      setIsShareCopied(true);
      setTimeout(() => setIsShareCopied(false), 2000); // 2秒后恢复原状
    });
  };
  
  // 将数据保存到本地存储sessionStorage
  useEffect(() => {
    sessionStorage.setItem('msgArr', JSON.stringify(msgArr));
    sessionStorage.setItem('history', JSON.stringify(history));
    // 检查是否需要滚动到底部
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [msgArr,history,currentStreamingMsg]);
  
  const isLastSystemMsg = (index) => {
    const lastMsg = msgArr[msgArr.length - 1];
    return lastMsg && !lastMsg.local && lastMsg.id === index.id;
  };

  return (
    <div className='talk'>
      <div className='input' ref={chatContainerRef}>
        <div className='showMsg'>
          {msgArr.map(index => (
            <ChatMsg key={index.id} index={index} isLastSystemMsg={isLastSystemMsg(index)} onShare={handleShareClick} setCurrentStreamingMsg={setCurrentStreamingMsg} />
          ))}
          {currentStreamingMsg && (
            <ChatMsg key={currentStreamingMsg.id} index={currentStreamingMsg} isLastSystemMsg={false} onShare={handleShareClick} />
          )}
        </div>
      </div>
      <div className="inputMsg">
        <div className="linkContainer" onMouseEnter={() => { setIsLinkHovered(true)}} onMouseLeave={() => { setIsLinkHovered(false)}}>
          <img className="linkIcon" src={isLinkHovered ? LinkHover : Link} alt="link" />
          {isLinkHovered && <div className="tooltip">支持上传文件（最多50个，每个100MB） 接受pdf、doc、xlsx、ppt、txt、图片等</div>}
        </div>
        <img
          className="voiceIcon"
          src={isRecording ? Key : Voice}
          alt="Voice"
          onClick={() => setIsRecording(!isRecording)}
        />
        {isRecording ? (
          <button className="inputarea">按住说话</button>
        ) : (
          <textarea
            className="inputarea"
            value={text}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder="在这里输入消息..."
          />
        )}
        <img
            className="sendIcon"
            src={Send}
            alt="Send"
            onClick={sendMassage}
          />
      </div>
      {isShareCopied && <div className="share-toast">链接已复制到剪贴板</div>}
    </div>
  )
};

export default Talk;