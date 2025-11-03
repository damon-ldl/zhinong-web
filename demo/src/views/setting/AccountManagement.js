import React,{ useState,useEffect } from 'react'
import '../../assets/styles/setting/basicseting.scss'
import { Button,Modal,message,Input} from 'antd'
import { useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import {  GetAccountInfoAPI,ChangePasswordAPI } from '../../request/api/index'

const AccountManagement = ()=> {
  const [modalOpen,setModalOpen] = useState(false)  // 修改密码弹窗
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [accountInfo, setAccountInfo] = useState({ username: '', nickname: '', email: '' });
  const dispatch = useDispatch()
  const navigate = useNavigate()

  useEffect(() => {
    const params = { username: sessionStorage.getItem('username') };
    GetAccountInfoAPI(params).then(res => {
      if (res.data.code === 200) {
        setAccountInfo({
          username: res.data.username,
          nickname: res.data.username,
          email: res.data.email
        });
      } else {
        message.error('获取账户信息失败');
      }
    });
  }, []);

  // 删除弹窗
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
  const onhandleConfirm = async () => {
    if (!oldPassword || !newPassword || !confirmPassword) {
      message.error('所有字段都是必需的');
      return;
    }

    if (newPassword !== confirmPassword) {
      message.error('新密码不一致');
      return;
    }

    const params = {
      username: accountInfo.username,
      oldPassword: oldPassword,
      newPassword: newPassword
    };

    ChangePasswordAPI(params).then(res => {
      if (res.data.code === 200) {
        message.success('修改成功, 请重新登录');
        setModalOpen(false);
        navigate('/login');
      } else if (res.data.code === 400) {
        message.error('原密码不正确');
      } else {
        message.error('修改失败，请重试');
      }
    }).catch(error => {
      message.error('修改失败，请重试');
    });
  };

  return (
    <div className='basicSetting'>
      <div className='theme'>
        <span>用户名:</span>
        <span className='userInfo'>{accountInfo.username}</span>
      </div>
      <div className='line'></div>
      <div className='language' style={{marginTop:'20px'}}>
        <span>昵称:</span>
        <span className='userInfo'>{accountInfo.nickname}</span>
      </div>
      <div className='line'></div>
      <div className='language' style={{marginTop:'20px'}}>
        <span>电子邮箱:</span>
        <span className='userInfo'>{accountInfo.email}</span>
      </div>
      <div className='line'></div>
      <div className='clearTalk' style={{marginTop:'20px'}}>
       <span>修改密码:</span>
       <Button  className='revise' onClick={onhandleClear}>修改</Button>
      </div>
      <Modal
        title="修改密码"
        centered
        open={modalOpen}
        width={400}
        footer={null}
        onCancel={onhandleModelClose}
      >
        <div className='line' style={{marginBottom:'10px'}}></div>
        <Input.Password className='passwordInput' placeholder="请输入原密码" value={oldPassword}
          onChange={(e) => setOldPassword(e.target.value)} />
        <Input.Password className='passwordInput' placeholder="请输入新密码" value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)} />
        <Input.Password className='passwordInput' placeholder="请再次输入新密码" value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)} />
        <div style={{marginTop:'20px'}}>
          <Button type="primary" danger className='confirmBtn' onClick={onhandleConfirm}>确认</Button>
          <Button className='CancelswitchBtn' onClick={onhandleModelClose} >取消</Button>
        </div>
      </Modal>              
    </div>
  )
}

export default AccountManagement