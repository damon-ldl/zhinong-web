// 创建reducer
import { legacy_createStore } from 'redux'
import reducer from './reducer'

// 创建容器
const store = legacy_createStore(reducer)


export default store