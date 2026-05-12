import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Form, Input, Button, Card, Typography, message, Select } from 'antd';
import { useAuthStore } from '../../store/authStore';

const { Title } = Typography;

/**
 * 注册页面
 */
const Register: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const { register } = useAuthStore();
  const navigate = useNavigate();

  const onFinish = async (values: { 
    username: string; 
    password: string; 
    confirmPassword: string;
    email: string;
    role: string;
  }) => {
    if (values.password !== values.confirmPassword) {
      message.error('两次输入的密码不一致');
      return;
    }

    setLoading(true);
    try {
      await register(values.username, values.password, values.email, values.role);
      message.success('注册成功，请登录');
      navigate('/login');
    } catch (error) {
      message.error('注册失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ 
      minHeight: '100vh', 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center',
      background: '#f0f2f5'
    }}>
      <Card style={{ width: 400, padding: '24px' }}>
        <Title level={2} style={{ textAlign: 'center' }}>算电协同平台</Title>
        <Title level={4} style={{ textAlign: 'center', marginBottom: '24px' }}>用户注册</Title>
        
        <Form onFinish={onFinish} layout="vertical">
          <Form.Item
            name="username"
            label="用户名"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input placeholder="请输入用户名" />
          </Form.Item>
          
          <Form.Item
            name="email"
            label="邮箱"
            rules={[
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' }
            ]}
          >
            <Input placeholder="请输入邮箱" />
          </Form.Item>
          
          <Form.Item
            name="role"
            label="账户类型"
            rules={[{ required: true, message: '请选择账户类型' }]}
          >
            <Select placeholder="请选择账户类型">
              <Select.Option value="user">普通用户</Select.Option>
              <Select.Option value="provider">算力提供方</Select.Option>
            </Select>
          </Form.Item>
          
          <Form.Item
            name="password"
            label="密码"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password placeholder="请输入密码" />
          </Form.Item>
          
          <Form.Item
            name="confirmPassword"
            label="确认密码"
            rules={[{ required: true, message: '请确认密码' }]}
          >
            <Input.Password placeholder="请再次输入密码" />
          </Form.Item>
          
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              注册
            </Button>
          </Form.Item>
        </Form>
        
        <div style={{ textAlign: 'center' }}>
          <Link to="/login">已有账号？立即登录</Link>
        </div>
      </Card>
    </div>
  );
};

export default Register;
