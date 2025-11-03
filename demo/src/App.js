import React from 'react'
import { useRoutes} from 'react-router-dom';
import router from './router'

function App() {
  const Outlet = useRoutes(router)
  return (
    <div className="App">
      {/* <Link to='/home'>Home</Link>
      <Link to='/about'>About</Link> */}
      {/* 类似于vue中的router-view */}
      {/* <Outlet></Outlet> */}
      {Outlet}
    </div>
  );
}

export default App;
