import React from 'react';
import ReactDOM from 'react-dom/client'
// 初始化样式---一般放在最前面
import "reset-css"
// UI框架样式

// 全局的样式
import "./assets/styles/global.scss"
// 组件的样式
import App from './App';
import { BrowserRouter } from 'react-router-dom'

// 状态管理
import { Provider } from 'react-redux'
import store from './store/index'

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <Provider store={store}>
    <BrowserRouter>
      <App/>
    </BrowserRouter>
  </Provider>
);
