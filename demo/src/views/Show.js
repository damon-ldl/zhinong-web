import React from 'react'
import { Button } from 'antd';
import { useNavigate} from 'react-router-dom'
import '../assets/styles/show.scss'
import centerPicture from '../assets/image/bg.png'
import LeftLogo from '../assets/image/leftLogo.png'
import { RightOutlined } from '@ant-design/icons';

export default function Show() {
  const navigate = useNavigate()
  return (
    <div className='initalPage'>
      <img src={LeftLogo} alt='leftLogo' className='leftLogo'></img>
      <Button className='rightLogo'>
        Contact Us
        <RightOutlined className='rightIcon' />
      </Button>  
      <div className='centerContent'>
        <img src={ centerPicture} alt='centerPicture' className='centerPicture' />
        <p className='centerText'>孙思邈中文医疗大模型(简称: Sunsimiao)希望能够遵循孙思邈的生平轨迹,重视民间医疗经验，不断累积中文医疗数据,并将数据附加给模型,致力于提供安全、可靠、普惠的中文医疗大模型。</p>
      </div>
      <Button type="primary"  className='StartButton' onClick={()=>{navigate('/home/talk')}}>
        GETSTART
        <RightOutlined className='rightIcon' />
      </Button>     
    </div>
  )
}
