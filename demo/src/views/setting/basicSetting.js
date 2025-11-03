import React,{ useState } from 'react'
import '../../assets/styles/setting/basicseting.scss'
import { Button,Dropdown,Space,Menu,Modal,message} from 'antd'
import { DownOutlined } from '@ant-design/icons';
import { useDispatch } from 'react-redux';

const BasicSetting = ()=> {
  const [modalOpen,setModalOpen] = useState(false)
  const dispatch = useDispatch()

  const onhandleClear = () =>{
    dispatch({type:'SET_MODALOPEN',payload:false})
    setTimeout(() => {
      setModalOpen(true) 
    }, 100);
  }

  const onhandleModelClose = () =>{
    setModalOpen(false)
    dispatch({type:'SET_MODALOPEN',payload:true})
  }
  const onhandleConfirm = () =>{
    setModalOpen(false)
    dispatch({type:'ClearTalk'})
    dispatch({type:'SET_MODALOPEN',payload:true})
    message.success('删除成功')
  }
  // 主题选择
  const themes = [
    {
      label: '系统',
      key: '0',
    },
    {
      label: '浅色',
      key: '1',
    },
    {
      label: '深色',
      key: '3',
    },
  ];

  const [selectedtheme, setSelectedTheme] = useState(themes[1].label);

  const handleMenuClick = (e) => {
    const selected = themes.find(theme => theme.key === e.key);
    if (selected) {
      setSelectedTheme(selected.label);
    }
  };
  const menuThem = (
    <Menu onClick={handleMenuClick}>
      {themes.map((theme) => (
        <Menu.Item
          key={theme.key}
          style={{
            color: theme.label === selectedtheme ? '#1A66FF' : 'black',
          }}
        >
          {theme.label}
        </Menu.Item>
      ))}
    </Menu>
  );

  // 语言选择
  const language = [
    {
      label: '自动检测',
      key: '0',
    },
    {
      label: '简体中文',
      key: '1',
    },
    {
      label: 'English',
      key: '3',
    },
    {
      label: 'dansk',
      key: '4',
    },
    {
      label: 'suomi',
      key: '5',
    },
    {
      label: 'Tagalog',
      key: '6',
    },
    {
      label: '繁体中文(香港)',
      key: '7',
    },
    {
      label: '繁体中文(台湾)',
      key: '8',
    }
  ];

  const [selectedLanguage, setSelectedLanguage] = useState(language[0].label);

  const handleLanguageClick = (e) => {
    const selected = language.find(theme => theme.key === e.key);
    if (selected) {
      setSelectedLanguage(selected.label);
    }
  };
  const menuLanguage = (
    <Menu onClick={handleLanguageClick}>
      {language.map((theme) => (
        <Menu.Item
          key={theme.key}
          style={{
            color: theme.label === selectedLanguage ? '#1A66FF' : 'black',
          }}
        >
          {theme.label}
        </Menu.Item>
      ))}
    </Menu>
  );

  // 声音选择

  return (
    <div className='basicSetting'>
      <div className='theme'>
        <span>主题</span>
        <Dropdown overlay={menuThem} trigger={['click']} className='dropdown'>
          <Space>
            {selectedtheme}
            <DownOutlined />
          </Space>
        </Dropdown>
      </div>
      <div className='line'></div>
      <div className='language' style={{marginTop:'20px'}}>
        <span>语言</span>
        <Dropdown overlay={menuLanguage} trigger={['click']} className='dropdown'>
          <Space>
            {selectedLanguage}
            <DownOutlined />
          </Space>
        </Dropdown>
      </div>
      <div className='line'></div>
      <div className='sound' style={{marginTop:'20px'}}>
        <span>声音</span>
      </div>
      <div className='line'></div>
      <div className='clearTalk' style={{marginTop:'20px'}}>
       <span>删除所有聊天</span>
       <Button type="primary" danger className='clearBtn' onClick={onhandleClear}>全部删除</Button>
      </div>
      <Modal
        title="确认提示"
        centered
        open={modalOpen}
        width={400}
        footer={null}
        onCancel={onhandleModelClose}
      >
        <div className='line'></div>
        <p style={{padding:'20px'}}>确认清楚您的历史聊天记录吗?</p>
        <div style={{marginTop:'20px'}}>
          <Button type="primary" danger className='clearBtn' onClick={onhandleConfirm}>确认删除</Button>
          <Button className='CancelBtn' onClick={onhandleModelClose} >取消</Button>
        </div>
      </Modal>            
    </div>
  )
}

export default BasicSetting