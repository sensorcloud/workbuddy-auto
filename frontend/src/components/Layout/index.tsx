import React from 'react';
import { Layout, Menu, Typography, Button, Space } from 'antd';
import { useNavigate, useLocation, Outlet } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import {
  HomeOutlined,
  ShopOutlined,
  CalendarOutlined,
  MonitorOutlined,
  DatabaseOutlined,
  FileTextOutlined,
  WalletOutlined,
  CreditCardOutlined,
  AlertOutlined,
  UserOutlined,
} from '@ant-design/icons';

const { Header, Sider, Content } = Layout;
const { Title } = Typography;

/**
 * 主布局组件
 * 包含侧边栏导航和顶部 header
 */
const LayoutComponent: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '首页',
    },
    {
      key: '/marketplace',
      icon: <ShopOutlined />,
      label: '算力市场',
    },
    {
      key: '/scheduling',
      icon: <CalendarOutlined />,
      label: '任务调度',
    },
    {
      key: '/monitoring',
      icon: <MonitorOutlined />,
      label: '监控中心',
    },
    {
      key: '/alert-rules',
      icon: <AlertOutlined />,
      label: '告警规则',
    },
    {
      key: '/assets',
      icon: <DatabaseOutlined />,
      label: '资产管理',
    },
    {
      key: '/orders',
      icon: <FileTextOutlined />,
      label: '订单管理',
    },
    {
      key: '/billing',
      icon: <CreditCardOutlined />,
      label: '账单中心',
    },
    {
      key: '/wallet',
      icon: <WalletOutlined />,
      label: '我的钱包',
    },
    {
      key: '/user',
      icon: <UserOutlined />,
      label: '用户中心',
    },
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider width={200} theme="dark">
        <div style={{ height: 64, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Title level={4} style={{ color: 'white', margin: 0 }}>
            算电协同
          </Title>
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Sider>
      
      <Layout>
        <Header style={{ background: '#fff', padding: '0 16px', display: 'flex', justifyContent: 'flex-end', alignItems: 'center' }}>
          <Space>
            <span>{user?.username || '用户'}</span>
            <Button type="link" onClick={handleLogout}>
              退出
            </Button>
          </Space>
        </Header>
        
        <Content style={{ margin: '16px', padding: '24px', background: '#fff', minHeight: 'auto' }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default LayoutComponent;
