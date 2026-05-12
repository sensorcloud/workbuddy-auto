import React, { useState } from 'react';
import {
  Card,
  Steps,
  Form,
  Input,
  Select,
  Radio,
  Button,
  Typography,
  Space,
  Alert,
  Spin,
  Descriptions,
  Tag,
  Row,
  Col,
  message,
} from 'antd';
import {
  CloudUploadOutlined,
  BulbOutlined,
  CheckCircleOutlined,
  ThunderboltOutlined,
  RocketOutlined,
  FireOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { apiService } from '@/services/api';
import type { Quote } from '@/types/order.types';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

type StrategyType = 'cheapest' | 'fastest' | 'greenest' | 'custom';

/**
 * 智能调度工作台
 * 用户提交计算任务，系统根据策略自动匹配最优算电组合并生成报价
 */
const SchedulingPage: React.FC = () => {
  const navigate = useNavigate();

  // 状态管理
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [gettingQuote, setGettingQuote] = useState(false);
  const [quotes, setQuotes] = useState<Quote[]>([]);
  const [selectedQuote, setSelectedQuote] = useState<Quote | null>(null);

  // 表单数据
  const [formData, setFormData] = useState({
    container_image: '',
    dataset_location: '',
    task_type: 'inference',
    estimated_duration_hours: 1,
    strategy: 'cheapest' as StrategyType,
  });

  /**
   * 步骤1：上传任务 - 验证任务参数
   */
  const handleTaskSubmit = async () => {
    if (!formData.container_image) {
      message.warning('请填写容器镜像');
      return;
    }

    setLoading(true);

    try {
      // 验证任务参数
      await apiService.post('/scheduling/validate', {
        container_image: formData.container_image,
        dataset_location: formData.dataset_location,
        task_type: formData.task_type,
        estimated_duration_hours: formData.estimated_duration_hours,
      });
      setCurrentStep(1);
      message.success('任务信息验证通过');
    } catch (error: any) {
      message.error(error.message || '任务信息验证失败');
    } finally {
      setLoading(false);
    }
  };

  /**
   * 步骤2：选择调度策略并获取报价
   */
  const handleGetQuote = async () => {
    setGettingQuote(true);

    try {
      const response = await apiService.post<{
        quotes: Quote[];
        recommended?: Quote;
      }>('/scheduling/quote', {
        task_type: formData.task_type,
        strategy: formData.strategy,
        estimated_duration_hours: formData.estimated_duration_hours,
      });

      const data = response.data;
      setQuotes(data?.quotes || []);
      setSelectedQuote(data?.recommended || null);
      setCurrentStep(2);

      message.success('报价生成成功');
    } catch (error: any) {
      message.error(error.message || '报价生成失败');
    } finally {
      setGettingQuote(false);
    }
  };

  /**
   * 步骤3：确认下单
   */
  const handleConfirmOrder = async () => {
    if (!selectedQuote) {
      message.warning('请选择一个报价方案');
      return;
    }

    setLoading(true);

    try {
      const response = await apiService.post<{ order_id: string; message: string }>(
        '/scheduling/tasks',
        {
          selected_quote: selectedQuote,
          container_image: formData.container_image,
          dataset_location: formData.dataset_location,
          task_type: formData.task_type,
          estimated_duration_hours: formData.estimated_duration_hours,
        }
      );

      const orderId = response.data?.order_id;
      message.success('订单创建成功，即将跳转到支付页面');
      setTimeout(() => {
        navigate(`/payment/${orderId}`);
      }, 1000);
    } catch (error: any) {
      message.error(error.message || '订单创建失败');
    } finally {
      setLoading(false);
    }
  };

  /**
   * 渲染报价卡片
   */
  const renderQuoteCard = (quote: Quote, isRecommended = false) => {
    return (
      <Card
        key={quote.asset_id}
        hoverable
        style={{
          marginBottom: 16,
          border: isRecommended ? '2px solid #1890ff' : '1px solid #d9d9d9',
        }}
        onClick={() => setSelectedQuote(quote)}
        className={selectedQuote?.asset_id === quote.asset_id ? 'selected-card' : ''}
      >
        {isRecommended && (
          <Tag color="blue" style={{ position: 'absolute', top: 10, right: 10 }}>
            推荐方案
          </Tag>
        )}

        <Row gutter={16}>
          <Col span={16}>
            <Title level={4}>
              {quote.match_reason || '智能匹配方案'}
            </Title>

            <Descriptions column={2} size="small">
              <Descriptions.Item label="算力成本">
                ¥{quote.compute_cost?.toFixed(2)}
              </Descriptions.Item>
              <Descriptions.Item label="能源成本">
                ¥{quote.energy_cost?.toFixed(2)}
              </Descriptions.Item>
              <Descriptions.Item label="预计碳减排">
                <Text type="success">
                  <FireOutlined /> {quote.carbon_saved_kg?.toFixed(2)} kg CO₂
                </Text>
              </Descriptions.Item>
            </Descriptions>
          </Col>

          <Col
            span={8}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'flex-end',
              justifyContent: 'center',
            }}
          >
            <Title level={2} style={{ color: '#f5222d', margin: 0 }}>
              ¥{quote.total_cost?.toFixed(2)}
            </Title>
            <Text type="secondary">总费用（{formData.estimated_duration_hours}小时）</Text>

            {selectedQuote?.asset_id === quote.asset_id && (
              <CheckCircleOutlined style={{ color: '#52c41a', fontSize: 24, marginTop: 8 }} />
            )}
          </Col>
        </Row>
      </Card>
    );
  };

  return (
    <div>
      <Title level={2}>智能调度工作台</Title>
      <Paragraph type="secondary">
        提交计算任务，系统自动匹配最优算电组合
      </Paragraph>

      {/* 步骤条 */}
      <Steps
        current={currentStep}
        items={[
          {
            title: '上传任务',
            icon: <CloudUploadOutlined />,
          },
          {
            title: '选择策略',
            icon: <BulbOutlined />,
          },
          {
            title: '确认报价',
            icon: <CheckCircleOutlined />,
          },
        ]}
        style={{ marginBottom: 32, marginTop: 24 }}
      />

      {/* 步骤1：上传任务 */}
      {currentStep === 0 && (
        <Card>
          <Form layout="vertical" onFinish={handleTaskSubmit}>
            <Form.Item label="容器镜像" required>
              <Input
                placeholder="例如：my-registry.com/my-image:latest"
                value={formData.container_image}
                onChange={(e) =>
                  setFormData({ ...formData, container_image: e.target.value })
                }
              />
            </Form.Item>

            <Form.Item label="数据集位置">
              <Input
                placeholder="例如：s3://my-bucket/dataset/"
                value={formData.dataset_location}
                onChange={(e) =>
                  setFormData({ ...formData, dataset_location: e.target.value })
                }
              />
            </Form.Item>

            <Form.Item label="任务类型">
              <Select
                value={formData.task_type}
                onChange={(value) => setFormData({ ...formData, task_type: value })}
                options={[
                  { label: '模型推理', value: 'inference' },
                  { label: '模型训练', value: 'training' },
                  { label: '视频渲染', value: 'render' },
                ]}
              />
            </Form.Item>

            <Form.Item label="预估时长（小时）">
              <Input
                type="number"
                min={0.5}
                step={0.5}
                value={formData.estimated_duration_hours}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    estimated_duration_hours: parseFloat(e.target.value) || 1,
                  })
                }
              />
            </Form.Item>

            <Form.Item>
              <Button type="primary" htmlType="submit" loading={loading} size="large">
                下一步：选择策略
              </Button>
            </Form.Item>
          </Form>
        </Card>
      )}

      {/* 步骤2：选择调度策略 */}
      {currentStep === 1 && (
        <Card>
          <Space direction="vertical" size={16} style={{ width: '100%' }}>
            <Title level={4}>选择调度策略</Title>

            <Radio.Group
              value={formData.strategy}
              onChange={(e) => setFormData({ ...formData, strategy: e.target.value })}
              style={{ width: '100%' }}
            >
              <Space direction="vertical" size={12} style={{ width: '100%' }}>
                <Radio value="cheapest" style={{ width: '100%' }}>
                  <Card size="small" style={{ width: '100%', marginLeft: 8 }}>
                    <Space>
                      <ThunderboltOutlined style={{ color: '#faad14', fontSize: 20 }} />
                      <div>
                        <Text strong>极致省钱</Text>
                        <br />
                        <Text type="secondary">自动匹配低价电力时段+竞价算力</Text>
                      </div>
                    </Space>
                  </Card>
                </Radio>

                <Radio value="fastest" style={{ width: '100%' }}>
                  <Card size="small" style={{ width: '100%', marginLeft: 8 }}>
                    <Space>
                      <RocketOutlined style={{ color: '#1890ff', fontSize: 20 }} />
                      <div>
                        <Text strong>快速完成</Text>
                        <br />
                        <Text type="secondary">优先匹配空闲算力，不计成本</Text>
                      </div>
                    </Space>
                  </Card>
                </Radio>

                <Radio value="greenest" style={{ width: '100%' }}>
                  <Card size="small" style={{ width: '100%', marginLeft: 8 }}>
                    <Space>
                      <FireOutlined style={{ color: '#52c41a', fontSize: 20 }} />
                      <div>
                        <Text strong>绿色环保</Text>
                        <br />
                        <Text type="secondary">优先匹配绿电+储能供电</Text>
                      </div>
                    </Space>
                  </Card>
                </Radio>
              </Space>
            </Radio.Group>

            <Space>
              <Button onClick={() => setCurrentStep(0)}>上一步</Button>
              <Button
                type="primary"
                icon={<BulbOutlined />}
                loading={gettingQuote}
                onClick={handleGetQuote}
              >
                获取智能报价
              </Button>
            </Space>
          </Space>
        </Card>
      )}

      {/* 步骤3：显示报价并确认下单 */}
      {currentStep === 2 && (
        <Spin spinning={gettingQuote}>
          <Space direction="vertical" size={16} style={{ width: '100%' }}>
            <Alert
              message="报价方案已生成"
              description="系统已根据您选择的策略生成最优报价方案，请选择并确认下单"
              type="success"
              showIcon
              style={{ marginBottom: 16 }}
            />

            {/* 推荐方案 */}
            {quotes.length > 0 && renderQuoteCard(quotes[0], true)}

            {/* 其他方案 */}
            {quotes.length > 1 && (
              <>
                <Title level={4}>其他可选方案</Title>
                {quotes.slice(1).map((quote) => renderQuoteCard(quote))}
              </>
            )}

            <Space>
              <Button onClick={() => setCurrentStep(1)}>上一步</Button>
              <Button
                type="primary"
                size="large"
                disabled={!selectedQuote}
                loading={loading}
                onClick={handleConfirmOrder}
              >
                确认下单
              </Button>
            </Space>
          </Space>
        </Spin>
      )}
    </div>
  );
};

export default SchedulingPage;
