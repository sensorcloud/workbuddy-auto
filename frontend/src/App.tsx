import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import Layout from './components/Layout';
import Home from './pages/Home';
import Marketplace from './pages/Marketplace';
import Scheduling from './pages/Scheduling';
import Monitoring from './pages/Monitoring';
import AssetManagement from './pages/AssetManagement';
import Orders from './pages/Orders';
import Payment from './pages/Payment';
import UserCenter from './pages/UserCenter';
import Login from './pages/UserCenter/Login';
import Register from './pages/UserCenter/Register';
import NotFound from './pages/NotFound';
import ErrorBoundary from './components/Common/ErrorBoundary';

/**
 * 路由守卫组件 - 保护需要认证的路由
 */
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuthStore();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
};

/**
 * 公共路由组件 - 已登录用户不能访问
 */
const PublicOnlyRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuthStore();
  
  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }
  
  return <>{children}</>;
};

function App() {
  return (
    <ErrorBoundary>
      <Routes>
        {/* 公共路由 */}
        <Route path="/login" element={<PublicOnlyRoute><Login /></PublicOnlyRoute>} />
        <Route path="/register" element={<PublicOnlyRoute><Register /></PublicOnlyRoute>} />
        
        {/* 受保护的路由 */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Home />} />
          <Route path="marketplace" element={<Marketplace />} />
          <Route path="scheduling" element={<Scheduling />} />
          <Route path="monitoring/:taskId?" element={<Monitoring />} />
          <Route path="assets" element={<AssetManagement />} />
          <Route path="orders" element={<Orders />} />
          <Route path="payment/:orderId" element={<Payment />} />
          <Route path="user" element={<UserCenter />} />
        </Route>
        
        {/* 404 */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </ErrorBoundary>
  );
}

export default App;
