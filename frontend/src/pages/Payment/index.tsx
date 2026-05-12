import React, { useState, useEffect } from 'react';
import {
  Card,
  Typography,
  Space,
  Button,
  Radio,
  message,
  Result,
  Spin,
  Descriptions,
  Tag,
} from 'antd';
import {
  CheckCircleOutlined,
  AlipayCircleFilled,
  WechatFilled,
} from '@ant-design/icons';
import { useParams, useNavigate } from 'react-router-dom';
import { apiService } from '@/services/api';

const { Title, Text, Paragraph } = Typography;

/**
 * 支付页面
 * 纯API调用，无mock数据
 */
const PaymentPage: React.FC = () => {
  const { orderId } = useParams();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(false);
  const [order, setOrder] = useState<any>(null);
  const [paymentMethod, setPaymentMethod] = useState<string>('balance');
  const [paid, setPaid] = useState(false);

  /**
   * 获取订单详情
   */
  const fetchOrder = async () => {
    if (!orderId) return;

    setLoading(true);
    try {
      const response = await apiService.get<any>(`/orders/${orderId}`);
      setOrder(response.data);
    } catch (error: any) {
      console.error('Failed to fetch order:', error);
      message.error('获取订单详情失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrder();
  }, [orderId]);

  /**
   * 处理支付 - 后端用PUT方法
   */
  const handlePay = async () => {
    if (!orderId) return;

    setLoading(true);
    try {
      // 后端支付端点是PUT方法
      const response = await apiService.put(`/orders/${orderId}/pay`, {});

      message.success('支付成功，任务即将开始执行');
      setPaid(true);
      setOrder(response.data || order);

      // 2秒后跳转到监控页面
      setTimeout(() => {
        navigate(`/monitoring/${orderId}`);
      }, 2000);
    } catch (error: any) {
      message.error(error?.message || '支付失败');
    } finally {
      setLoading(false);
    }
  };

  if (paid) {
    return (
      <div style={{ maxWidth: 600, margin: '100px auto' }}>
        <Result
          status="success"
          title="支付成功！"
          subTitle="订单已支付，即将跳转到任务监控页面"
          extra={[
            <Button
              type="primary"
              key="monitor"
              onClick={() => navigate(`/monitoring/${orderId}`)}
            >
              立即查看监控
            </Button>,
            <Button key="orders" onClick={() => navigate('/orders')}>
              返回订单列表
            </Button>,
          ]}
        />
      </div>
    );
  }

  if (!order) {
    return (
      <Spin spinning={loading} style={{ display: 'flex', justifyContent: 'center', marginTop: 100 }}>
        <div />
      </Spin>
    );
  }

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      <Title level={2}>支付订单</Title>
      <Paragraph type="secondary">
        请选择支付方式并完成支付
      </Paragraph>

      <Spin spinning={loading}>
        {/* 订单信息 */}
        {order && (
          <Card style={{ marginBottom: 24 }}>
            <Descriptions column={1} bordered>
              <Descriptions.Item label="订单ID">
                {orderId}
              </Descriptions.Item>
              <Descriptions.Item label="任务类型">
                {order.task_type || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="策略">
                <Tag>{order.strategy || '-'}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="预估时长">
                {order.estimated_duration_hours || 0} 小时
              </Descriptions.Item>
              {order.selected_quote && (
                <Descriptions.Item label="总费用">
                  <Text strong style={{ fontSize: 20, color: '#f5222d' }}>
                    ¥{order.selected_quote.total_cost?.toFixed(2) || '0.00'}
                  </Text>
                </Descriptions.Item>
              )}
            </Descriptions>
          </Card>
        )}

        {/* 支付方式选择 */}
        <Card title="选择支付方式" style={{ marginBottom: 24 }}>
          <Radio.Group
            value={paymentMethod}
            onChange={(e) => setPaymentMethod(e.target.value)}
            style={{ width: '100%' }}
          >
            <Space direction="vertical" style={{ width: '100%' }} size={16}>
              <Radio value="balance" style={{ width: '100%' }}>
                <Card size="small" hoverable style={{ marginLeft: 8 }}>
                  <Space>
                    <CheckCircleOutlined
                      style={{ color: '#1890ff', fontSize: 24 }}
                    />
                    <div>
                      <Text strong>余额支付</Text>
                      <br />
                      <Text type="secondary">使用账户余额支付</Text>
                    </div>
                  </Space>
                </Card>
              </Radio>

              <Radio value="alipay" style={{ width: '100%' }}>
                <Card size="small" hoverable style={{ marginLeft: 8 }}>
                  <Space>
                    <AlipayCircleFilled
                      style={{ color: '#1677ff', fontSize: 24 }}
                    />
                    <div>
                      <Text strong>支付宝</Text>
                      <br />
                      <Text type="secondary">使用支付宝扫码支付</Text>
                    </div>
                  </Space>
                </Card>
              </Radio>

              <Radio value="wechat" style={{ width: '100%' }}>
                <Card size="small" hoverable style={{ marginLeft: 8 }}>
                  <Space>
                    <WechatFilled
                      style={{ color: '#07c160', fontSize: 24 }}
                    />
                    <div>
                      <Text strong>微信支付</Text>
                      <br />
                      <Text type="secondary">使用微信扫码支付</Text>
                    </div>
                  </Space>
                </Card>
              </Radio>
            </Space>
          </Radio.Group>
        </Card>

        {/* 支付按钮 */}
        <Card>
          <Space direction="vertical" style={{ width: '100%' }} size={16}>
            <div style={{ textAlign: 'right' }}>
              <Text>应付金额：</Text>
              <Text strong style={{ fontSize: 24, color: '#f5222d' }}>
                ¥{order?.selected_quote?.total_cost?.toFixed(2) || '0.00'}
              </Text>
            </div>

            <Button
              type="primary"
              size="large"
              block
              loading={loading}
              onClick={handlePay}
            >
              确认支付
            </Button>
          </Space>
        </Card>
      </Spin>
    </div>
  );
};

export default PaymentPage;
