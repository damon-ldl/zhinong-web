import React,{ useState} from 'react'
import '../../assets/styles/setting/basicseting.scss'
import { Button,Modal,message,Switch} from 'antd'
import { useDispatch, useSelector} from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { DeleteAccountAPI } from '../../request/api/index'

const DataManagement = ()=> {
  const [modalOpen,setModalOpen] = useState(false)  // 删除弹窗
  const [switchOpen,setSwitchOpen] = useState(false)  // 开关弹窗
  const [switchChecked, setSwitchChecked] = useState(false); // 开关状态
  const [tempSwitchChecked, setTempSwitchChecked] = useState(false); // 临时开关状态
  const msgArr = useSelector(state => state.msgArr)  // 获取消息数组---为导出数据做准备 
  const dispatch = useDispatch()
  const navigate = useNavigate()

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
  const onhandleConfirm = () =>{
    const params = { username: sessionStorage.getItem('username')};
    DeleteAccountAPI(params).then(res =>{
      if(res.data.code === 200){
        setModalOpen(false)
        navigate('/login')
        message.success('删除成功')  
      } else {
        message.error("删除失败");
      }
    }).catch(err =>{
      message.error("请求失败");
    })
  }

  // 开关弹窗
  const onhandleChange = () => {
    setTempSwitchChecked(!switchChecked);
    dispatch({ type: 'SET_MODALOPEN', payload: false });
    setTimeout(() => {
      setSwitchOpen(true);
    }, 100);
  };

  const onhandleSwitchClose = () => {
    setSwitchOpen(false);
    dispatch({ type: 'SET_MODALOPEN', payload: true });
  };

  const onhandleSwitchConfirm = () => {
    setSwitchOpen(false);
    setSwitchChecked(tempSwitchChecked);
    dispatch({ type: 'SET_MODALOPEN', payload: true });
  };

  // 导出数据
  const exportRecords = () => {
    const content = msgArr.map(item => item.msg).join('\n');
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'chat_records.txt';
    a.click();
    URL.revokeObjectURL(url);
}

  return (
    <div className='basicSetting'>
      <div className='theme'>
        <span>为所有用户改进模型</span>
        <div className='switchOperate'>
          <span style={{fontSize:'14px',fontWeight:'400',marginRight:'10px'}}>
            {switchChecked ? '开' : '关'}
          </span>
          <Switch size='small' checked={switchChecked} onChange={onhandleChange} />
        </div>
      </div>
      <div className='line'></div>
      <div className='language' style={{marginTop:'20px'}}>
        <span>导出数据</span>
        <Button className='export' onClick={exportRecords} >导出</Button>
      </div>
      <div className='line'></div>
      <div className='clearTalk' style={{marginTop:'20px'}}>
       <span>删除账户</span>
       <Button type="primary" danger className='Delete' onClick={onhandleClear}>删除</Button>
      </div>
      <Modal
        title="确认删除账户吗?"
        centered
        open={modalOpen}
        width={400}
        footer={null}
        onCancel={onhandleModelClose}
      >
        <div className='line'></div>
        <div style={{padding:'20px 20px 0px 20px'}}>• 删除账户为永久操作，且无法撤销。</div>
        <div style={{padding:'10px 20px 0px 20px'}}>• 删除后，您将无法访问该服务。</div>
        <div style={{padding:'10px 20px 0px 20px'}}>• 您无法使用同一电子邮箱地址创建新用户。</div>
        <div style={{marginTop:'20px'}}>
          <Button type="primary" danger className='clearDeleteBtn' onClick={onhandleConfirm}>确认</Button>
          <Button className='CancelswitchBtn' onClick={onhandleModelClose} >取消</Button>
        </div>
      </Modal> 
      <Modal
        title="模型改进"
        centered
        open={switchOpen}
        width={400}
        footer={null}
        onCancel={onhandleModelClose}
      >
        <div className='line'></div>
        <p style={{padding:'20px',fontSize:'16px',fontWeight:'500',color:'#1B1F26'}}>
          为所有用户改进模型
        </p>
        <p style={{padding:'20px',marginTop:'-10px'}}>允许我们将您的内容用于训练我们的模型，这样可以优化您和其他用户的使用体验。我们将采取措施保护您的隐私。</p>
        <div style={{marginTop:'20px'}}>
          <Button type="primary" danger className='confirmBtn' onClick={onhandleSwitchConfirm}>确认</Button>
          <Button className='CancelswitchBtn' onClick={onhandleSwitchClose} >取消</Button>
        </div>
      </Modal>              
    </div>
  )
}

export default DataManagement