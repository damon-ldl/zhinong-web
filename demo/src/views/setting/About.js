import React from 'react'
// 引入logo
import Logo from '../../assets/image/logo.png'
import '../../assets/styles/setting/about.scss'

const About = () => {
  return (
    <div className='about'>
      <img src={Logo} alt="logo" className='logo' />
      <div className='title'>版权由心动实验室(X-D Lab)所有!</div>
      <div className='version'>版本号:1.0.1</div>
    </div>
  )
}

export default About