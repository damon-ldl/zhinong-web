import React from 'react';
import { Layout, theme,Menu,Dropdown,Avatar,Modal} from 'antd';
import { Outlet,useNavigate,useLocation} from 'react-router-dom'
import '../assets/styles/home.scss'
import { useState } from 'react';
import { useSelector,useDispatch } from 'react-redux';
// 图片的导入
import userHead from '../assets/image/userHead.png'
import Sidercontrol from '../assets/image/sider.png'
import Setting from '../assets/image/setting.png'
import Change from '../assets/image/change.png'
// 引入侧边栏内容
import SiderContent from '../components/TalkHistoryside'
// 引入参数设置弹窗的图片
import Set from '../assets/image/set.png'
import Data from '../assets/image/data.png'
import User from '../assets/image/zhanghao.png'
import About from '../assets/image/about.png'
// 引入设置弹窗的各内容界面 ------ 参数设置页面的抽离
import BasicSetting from '../views/setting/basicSetting'
import DataManagement from '../views/setting/DataManagement'
import AccountManagement from '../views/setting/AccountManagement'
import AboutSetting from '../views/setting/About'


const {Header,Content, Sider } = Layout;
const Home = () => {
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  const [collapsed, setCollapsed] = useState(true); // 侧边栏显示状态，默认为隐藏
  const modalOpen = useSelector(state => state.ModalOpen)// 控制参数配置弹窗的显示与否
  const [selectedOption, setSelectedOption] = useState('general');

  const navigate = useNavigate()
  const location = useLocation()
  const dispatch = useDispatch()
    // 退出按钮
    const loginOut = () =>{
      navigate('/login')
  
    }

  const menu = (
    <Menu>
      <Menu.Item key="logout"  onClick={loginOut} className="logout">
         退出
      </Menu.Item>
    </Menu>
  );

  const onhandleModelOpen = () =>{
    dispatch({type:'SET_MODALOPEN',payload:true})
  }

  const onhandleModelClose = () =>{
    dispatch({type:'SET_MODALOPEN',payload:false})
  }

  // 点击选项时更新选中状态
  const handleOptionClick = (option) => {
    setSelectedOption(option);
  };

  // 根据选项返回对应的组件
  const getContentComponent = () => {
    switch (selectedOption) {
      case 'general':
        return <BasicSetting />;
      case 'data':
        return <DataManagement />;
      case 'account':
        return <AccountManagement />;
      case 'about':
        return <AboutSetting />;
      default:
        return null;
    }
  };

  return (
    <Layout
      style={{
        minHeight: '100vh',
      }}>
      <Sider
          style={{
              borderRight: '1px solid rgba(229, 231, 235, 1)',
              overflow: 'hidden', // 确保侧边栏隐藏时不显示内容
              width: collapsed ? '0' : '200px', // 根据 collapsed 状态设置宽度
              marginLeft: collapsed ? '-80px' : '0', // 根据 collapsed 状态设置左边距
          }}
          collapsed={collapsed}
          onCollapse={(collapsed) => setCollapsed(collapsed)}
      >
        <SiderContent />
      </Sider>
      <Layout>
        <Header
          style={{
            height:'50px',
            borderBottom: '1px solid rgba(229, 231, 235, 1)',
          }}
        >
        <img src={Sidercontrol} alt='展开' className='sidercontrol' onClick={() => setCollapsed(!collapsed)} />
        <div style={{float:'right',marginRight:'18px',marginTop:'-8px'}}>
          <Dropdown overlay={menu}>
            <Avatar  src={userHead} style={{width:'24px',height:'24px'}} />
          </Dropdown>
        </div>
        {location.pathname==='/home/talk' &&(
          <div style={{float:'right'}}>
            <img src={Setting} alt='设置' className='HeaderIcon' onClick={onhandleModelOpen}/>
            <img src={Change} alt='数字人' className='HeaderIcon' />
          </div>
        )}
        </Header>
        <Content
          style={{
            margin: 0,
            background: colorBgContainer,
            borderRadius: borderRadiusLG,
          }}
        >
          <Outlet></Outlet>
        </Content>
      </Layout>
      <Modal
        title={<div style={{ textAlign: 'center' }}>设置</div>}
        centered
        open={modalOpen}
        footer={null}
        onCancel={onhandleModelClose}
        width={600} // 自定义宽度
        style={{borderRadius:'6px'}} // 自定义背景色
        className='modal'
      >
        <div className='modal-content'>
          <div className='left-operate'>
            <p className={selectedOption === 'general' ? 'selected' : ''}onClick={() => handleOptionClick('general')}>
              <img src={Set} alt='设置'/>通用设置
            </p>
            <p className={selectedOption === 'data' ? 'selected' : ''}onClick={() => handleOptionClick('data')}>
              <img src={Data} alt='数据'/>数据管理
            </p>
            <p className={selectedOption === 'account' ? 'selected' : ''}onClick={() => handleOptionClick('account')}>
              <img src={User} alt='账号'/>账号管理
            </p>
            <p className={selectedOption === 'about' ? 'selected' : ''}onClick={() => handleOptionClick('about')}>
              <img src={About} alt='关于' style={{marginLeft:'-24px'}}/>关于
            </p>
          </div>
          <div className='right-content'>{getContentComponent()}</div>
        </div>
      </Modal>
    </Layout>
  );
};
export default Home;