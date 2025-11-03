import React, { useState, useEffect } from 'react';
import '../assets/styles/TalkHistory.scss';
import { useDispatch } from 'react-redux';
import { Button, Input, Tooltip ,message} from 'antd';
import { PlusOutlined, SearchOutlined } from '@ant-design/icons';
import { ChatHistoryAPI } from '../request/api/index'
 
const TalkHistoryside = () => {
    const dispatch = useDispatch();

    const [searchKeyword, setSearchKeyword] = useState('');
    const [filteredHistory, setFilteredHistory] = useState([]);
    const [history, setHistory] = useState([]);

    useEffect(() => {
        const fetchChatHistory = async () => {
            const username = sessionStorage.getItem('username');
            if (!username) {
                message.error('未找到用户名，请重新登录');
                return;
            }

            try {
                const res = await ChatHistoryAPI({ username });
                if (res.data.code === 200) {
                    setHistory(res.data.history);
                    setFilteredHistory(res.data.history);
                } else {
                    message.error('获取历史对话记录失败');
                }
            } catch (error) {
                message.error('获取历史对话记录失败');
            }
        };

        fetchChatHistory();
    }, []);

    // const history = React.useMemo(() => [
    //     [
    //         { id: new Date().getTime(), msg: "我没有感到腹部明显疼痛,请问还需要检查什么吗?", local: true},
    //         { id: new Date().getTime(), msg: "Hi! How can I help you?", local: false},
    //         { id: new Date().getTime(), msg: "I'm looking for information on...", local: true },
    //         { id: new Date().getTime(), msg: "Sure, I can assist you with that.", local: false }
    //     ],
    //     [
    //         { id: new Date().getTime(), msg: "晚上着凉了，肚子疼怎么办,阿达大大", local: true },
    //         { id: new Date().getTime(), msg: "Hello! What's up?", local: false },
    //         { id: new Date().getTime(), msg: "Not much, just browsing.", local: true },
    //         { id: new Date().getTime(), msg: "Okay, let me know if you need anything.", local: false }
    //     ],
    //     [
    //         { id: new Date().getTime(), msg: "你好！", local: true },
    //         { id: new Date().getTime(), msg: "Morning! How are you?", local: false },
    //         { id: new Date().getTime(), msg: "I'm good, thanks!", local: true },
    //         { id: new Date().getTime(), msg: "Great to hear!", local: false }
    //     ]
    // ], []);

    useEffect(() => {
        if (searchKeyword) {
            setFilteredHistory(history.filter(conversation => 
                conversation.some(msg => msg.msg.includes(searchKeyword))
            ));
        } else {
            setFilteredHistory(history);
        }
    }, [searchKeyword, history]);

    const handleHistoryClick = (conversation) => {
        dispatch({ type: 'ClearMsg' }); // 更新会话状态
        // 添加延迟
        setTimeout(() => {
            dispatch({ type: 'SetMsg', payload: conversation }); // 更新会话状态
        }, 100); // 1秒延迟
    };

    const onAddTalk = () => {
        dispatch({ type: 'ClearMsg' });
    };

    const handleSearchChange = (e) => {
        setSearchKeyword(e.target.value);
    };

    return (
        <div className="scrollable">
            <Button className='add-talk' type='primary' icon={<PlusOutlined />} onClick={onAddTalk}>
                新建对话
            </Button>
            <Input className='search'
                placeholder="请输入关键字搜索"
                value={searchKeyword}
                onChange={handleSearchChange}
                suffix={
                    <Tooltip title="搜索">
                        <SearchOutlined
                            style={{
                                color: 'rgba(0,0,0,.45)',
                            }}
                        />
                    </Tooltip>
                }
            />
            <div className="talk-history-container">
                {filteredHistory.map((conversation, index) => (
                    <div key={index} className='talk-history-item' onClick={() => handleHistoryClick(conversation)}>
                        {conversation.length > 0 && (
                            <p>{conversation[0].msg.substring(0, 10)}...</p>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default TalkHistoryside;
