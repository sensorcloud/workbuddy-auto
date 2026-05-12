import React from 'react';
import { Card, Row, Col, Typography, Space, Button } from 'antd';
import {
  ShopOutlined,
  ControlOutlined,
  MonitorOutlined,
  DatabaseOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const { Title, Text, Paragraph } = Typography;

/**
 * 首页
 * 平台功能概览和快速入口
 */
const HomePage: React.FC = () => {
  const navigate = useNavigate();

  /**
   * 功能卡片配置
   */
  const featureCards = [
    {
      title: '资源市场',
      description: '浏览和搜索可用的算力与能源资源，支持多维度筛选',
      icon: <ShopOutlined style={{ fontSize: 48, color: '#1890ff' }} />,
      path: '/marketplace',
      color: '#e6f7ff',
    },
    {
      title: '智能调度',
      description: '提交计算任务，系统自动匹配最优算电组合',
      icon: <ControlOutlined style={{ fontSize: 48, color: '#52c41a' }} />,
      path: '/scheduling',
      color: '#f6ffed',
    },
    {
      title: '任务监控',
      description: '实时监控任务状态、功耗和碳排放数据',
      icon: <MonitorOutlined style={{ fontSize: 48, color: '#faad14' }} />,
      path: '/monitoring',
      color: '#fff7e6',
    },
    {
      title: '资产管理',
      description: '管理您的算力和能源资产，查看收益情况',
      icon: <DatabaseOutlined style={{ fontSize: 48, color: '#f5222d' }} />,
      path: '/assets',
      color: '#fff1f0',
    },
  ];

  return (
    <div>
      {/* 欢迎区域 */}
      <div
        style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          padding: '60px 24px',
          borderRadius: 8,
          marginBottom: 32,
          textAlign: 'center',
        }}
      >
        <Title level={1} style={{ color: '#fff', marginBottom: 16 }}>
          欢迎使用算电协同工作台
        </Title>
        <Paragraph style={{ color: '#fff', fontSize: 18, marginBottom: 24 }}>
          通过电力价格信号智能调度算力交易，实现成本优化与绿色计算
        </Paragraph>
        <Space size={16}>
          <Button
            type="primary"
            size="large"
            icon={<ThunderboltOutlined />}
            onClick={() => navigate('/scheduling')}
            style={{ background: '#52c41a', borderColor: '#52c41a' }}
          >
            立即开始
          </Button>
          <Button
            size="large"
            style={{ color: '#fff', borderColor: '#fff' }}
            onClick={() => navigate('/marketplace')}
          >
            浏览资源
          </Button>
        </Space>
      </div>

      {/* 功能概览 */}
      <Title level={3} style={{ marginBottom: 24 }}>
        核心功能
      </Title>

      <Row gutter={[24, 24]}>
        {featureCards.map((card) => (
          <Col xs={24} sm={12} md={6} key={card.path}>
            <Card
              hoverable
              onClick={() => navigate(card.path)}
              style={{ height: '100%', background: card.color }}
            >
              <Space direction="vertical" size={16} style={{ width: '100%' }}>
                {card.icon}
                <Title level={4} style={{ margin: 0 }}>
                  {card.title}
                </Title>
                <Text type="secondary">{card.description}</Text>
              </Space>
            </Card>
          </Col>
        ))}
      </Row>

      {/* 平台优势 */}
      <Title level={3} style={{ marginTop: 48, marginBottom: 24 }}>
        为什么选择我们
      </Title>

      <Row gutter={[24, 24]}>
        <Col span={8}>
          <Card>
            <Title level={4}>💰 极致省钱</Title>
            <Paragraph type="secondary">
              通过智能调度匹配低价电力时段和竞价算力，最高可节省70%成本
            </Paragraph>
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Title level={4}>🌿 绿色环保</Title>
            <Paragraph type="secondary">
              优先匹配绿电+储能供电，提供碳足迹报告和减排证明
            </Paragraph>
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Title level={4}>⚡ 快速部署</Title>
            <Paragraph type="secondary">
              支持容器化任务提交，秒级资源匹配，分钟级任务启动
            </Paragraph>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default HomePage;
