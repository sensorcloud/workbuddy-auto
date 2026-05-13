import { Routes, Route, Navigate, Outlet } from 'react-router-dom';
import Home from '@/pages/Home';
import Marketplace from '@/pages/Marketplace';
import AssetDetail from '@/pages/AssetDetail';
import Scheduling from '@/pages/Scheduling';
import Monitoring from '@/pages/Monitoring';
import AlertRules from '@/pages/AlertRules';
import AssetManagement from '@/pages/AssetManagement';
import Orders from '@/pages/Orders';
import OrderDetail from '@/pages/OrderDetail';
import Payment from '@/pages/Payment';
import Billing from '@/pages/Billing';
import Wallet from '@/pages/Wallet';
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
        <Route path="assets/:assetId" element={<AssetDetail />} />
        <Route path="scheduling" element={<Scheduling />} />
        <Route path="monitoring" element={<Monitoring />} />
        <Route path="monitoring/:taskId" element={<Monitoring />} />
        <Route path="alert-rules" element={<AlertRules />} />
        <Route path="assets" element={<AssetManagement />} />
        <Route path="orders" element={<Orders />} />
        <Route path="orders/:orderId" element={<OrderDetail />} />
        <Route path="payment/:orderId" element={<Payment />} />
        <Route path="billing" element={<Billing />} />
        <Route path="wallet" element={<Wallet />} />
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
const RequireAuth = () => {
  const token = localStorage.getItem('access_token');
  
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  
  return <Outlet />;
};

export default AppRoutes;
