// 路由的懒加载的写法
import Home from '../views/Home'
import Login from '../views/login/index'
import React, { lazy } from 'react'
// 实现重定向的功能
import { Navigate } from 'react-router-dom'
import { useSelector } from 'react-redux'

// 懒加载的形式
const Talk = lazy(()=>import('../views/talk/index'))
const Show = lazy(()=>import('../views/Show'))

// 懒加载的形式外面必须套一层loading的提示加载组件
const withLoadingComponent = (comp)=>(
    <React.Suspense fallback={<div>Loading...</div>}>
        {comp}
    </React.Suspense>
)

// 私有路由组件
const PrivateRoute = ({ element }) => {
    // const isLoggedIn = useSelector(state=>state.loginFlag)
    const isLoggedIn = true; // 假设用户已经登录
    if (!isLoggedIn) {
      // 如果用户未登录，重定向到登录页面
      return <Navigate to="/login" />;
    }
    // 如果用户已经登录，则允许访问传入的元素（即 <List/> 页面）
    return element;
  };


const routes = [
    {
        path:'/',
        element: <Navigate to="/login" />
    },
    {
        path:'/home',
        element: <Home/>,
        children:[
            {
                path: '',
                element: <Navigate to="show" /> // 添加这个重定向
            },
            {
                path:'show',
                element:withLoadingComponent(<PrivateRoute element={<Show/>} />)
            },
            {
                path:'talk',
                element:withLoadingComponent(<PrivateRoute element={<Talk/>} />)
            }
        ]
    },
    {
        path:'/login',
        element:<Login/>
    },
    {
        path:'*',
        element: <Navigate to="/login" />
    },
]

export default routes