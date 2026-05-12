import { Routes, Route } from 'react-router-dom';
import Home from '@/pages/Home';
import Marketplace from '@/pages/Marketplace';
import Scheduling from '@/pages/Scheduling';
import Monitoring from '@/pages/Monitoring';
import AssetManagement from '@/pages/AssetManagement';
import Orders from '@/pages/Orders';
import Payment from '@/pages/Payment';
import UserCenter from '@/pages/UserCenter';
import Login from '@/pages/UserCenter/Login';
import Register from '@/pages/UserCenter/Register';
import NotFound from '@/pages/NotFound';

/**
 * 应用路由配置
 * 包含路由守卫逻辑
 */
const AppRoutes = () => {
  return (
    <Routes>
      {/* 公共路由 */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      
      {/* 受保护的主路由 */}
      <Route path="/" element={<RequireAuth />}>
        <Route index element={<Home />} />
        <Route path="marketplace" element={<Marketplace />} />
        <Route path="scheduling" element={<Scheduling />} />
        <Route path="monitoring/:taskId?" element={<Monitoring />} />
        <Route path="assets" element={<AssetManagement />} />
        <Route path="orders" element={<Orders />} />
        <Route path="payment/:orderId" element={<Payment />} />
        <Route path="user" element={<UserCenter />} />
        <Route path="user/settings" element={<UserCenter />} />
      </Route>
      
      {/* 404 */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
};

/**
 * 路由守卫组件
 */
const RequireAuth = ({ children }: { children: JSX.Element }) => {
  const token = localStorage.getItem('access_token');
  
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

export default AppRoutes;
