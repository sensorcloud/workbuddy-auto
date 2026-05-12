import React from 'react';
import { useAuthStore } from '../../store/authStore';
import { Card, Button, Descriptions, Tag, Typography } from 'antd';

const { Title, Text } = Typography;

/**
 * 用户中心页面
 * 展示用户信息和账户状态
 */
const UserCenter: React.FC = () => {
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    window.location.href = '/login';
  };

  return (
    <div style={{ padding: '24px', maxWidth: '800px', margin: '0 auto' }}>
      <Title level={2}>用户中心</Title>
      
      <Card style={{ marginTop: '24px' }}>
        <Descriptions title="基本信息" bordered column={2}>
          <Descriptions.Item label="用户名">{user?.username || '未登录'}</Descriptions.Item>
          <Descriptions.Item label="邮箱">{user?.email || '-'}</Descriptions.Item>
          <Descriptions.Item label="账户类型">
            <Tag color="blue">{user?.role || '用户'}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="账户状态">
            <Tag color="green">正常</Tag>
          </Descriptions.Item>
        </Descriptions>
      </Card>

      <Card title="操作" style={{ marginTop: '24px' }}>
        <Button type="primary" danger onClick={handleLogout}>
          退出登录
        </Button>
      </Card>
    </div>
  );
};

export default UserCenter;
