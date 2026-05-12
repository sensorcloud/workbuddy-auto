import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Card,
  Row,
  Col,
  Typography,
  Space,
  Spin,
  Alert,
  Button,
  Descriptions,
  Tag,
  Timeline,
  message,
} from 'antd';
import {
  ThunderboltOutlined,
  CloudOutlined,
  MoneyCollectOutlined,
  ClockCircleOutlined,
  PauseCircleOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';
import { useParams, useNavigate } from 'react-router-dom';
import ReactECharts from 'echarts-for-react';
import { apiService } from '@/services/api';
import type { TaskStatus } from '@/types/order.types';

const { Title, Text, Paragraph } = Typography;

/**
 * 任务监控面板
 * 实时显示功耗、碳排放、任务日志等信息
 */
const MonitoringPage: React.FC = () => {
  const { taskId } = useParams();
  const navigate = useNavigate();

  // 状态管理
  const [loading, setLoading] = useState(false);
  const [taskStatus, setTaskStatus] = useState<TaskStatus | null>(null);
  const [powerData, setPowerData] = useState<number[]>([]);
  const [carbonData, setCarbonData] = useState<number[]>([]);
  const [timeLabels, setTimeLabels] = useState<string[]>([]);
  const [logs, setLogs] = useState<string[]>([]);
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timer | null>(null);

  /**
   * 获取任务状态和监控数据
   */
  const fetchTaskStatus = useCallback(async (taskId: string) => {
    try {
      const response = await apiService.get<TaskStatus>(
        `/monitoring/tasks/${taskId}`
      );
      const data = response.data;
      setTaskStatus(data || null);

      // 如果后端返回实时指标，更新图表数据
      if (data?.real_time_metrics) {
        setPowerData(data.real_time_metrics.power_kw || []);
        setCarbonData(data.real_time_metrics.carbon_kg || []);
      }

      // 如果后端返回时间戳，更新时间标签
      if (data?.real_time_metrics?.timestamps) {
        setTimeLabels(data.real_time_metrics.timestamps);
      } else {
        // 生成模拟时间标签
        const now = new Date();
        const labels = [];
        for (let i = 9; i >= 0; i--) {
          const t = new Date(now.getTime() - i * 60000);
          labels.push(t.toTimeString().slice(0, 5));
        }
        setTimeLabels(labels);
      }
    } catch (error: any) {
      console.error('Failed to fetch task status:', error);
      message.error('获取任务状态失败');
    }
  }, []);

  /**
   * 启动轮询
   */
  const startPolling = useCallback((taskId: string) => {
    // 先立即获取一次
    fetchTaskStatus(taskId);

    // 每5秒轮询一次
    const interval = setInterval(() => {
      fetchTaskStatus(taskId);
    }, 5000);

    setPollingInterval(interval);
  }, [fetchTaskStatus]);

  // 初始加载和轮询
  useEffect(() => {
    if (!taskId) return;

    setLoading(true);
    startPolling(taskId);
    setLoading(false);

    // 清理轮询
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
        setPollingInterval(null);
      }
    };
  }, [taskId, startPolling]);

  /**
   * 功耗曲线图配置
   */
  const getPowerChartOption = () => ({
    title: {
      text: '实时功耗曲线（过去1小时）',
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
    },
    xAxis: {
      type: 'category',
      data: timeLabels.length > 0 ? timeLabels : ['暂无数据'],
    },
    yAxis: {
      type: 'value',
      name: '功率 (kW)',
    },
    series: [
      {
        name: '功耗',
        type: 'line',
        data: powerData.length > 0 ? powerData : [0],
        smooth: true,
        areaStyle: {
          opacity: 0.3,
        },
        lineStyle: {
          color: '#1890ff',
        },
        itemStyle: {
          color: '#1890ff',
        },
      },
    ],
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
  });

  /**
   * 碳排放曲线图配置
   */
  const getCarbonChartOption = () => ({
    title: {
      text: '实时碳排放曲线',
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
    },
    xAxis: {
      type: 'category',
      data: timeLabels.length > 0 ? timeLabels : ['暂无数据'],
    },
    yAxis: {
      type: 'value',
      name: '碳排放 (kg CO₂)',
    },
    series: [
      {
        name: '碳排放',
        type: 'line',
        data: carbonData.length > 0 ? carbonData : [0],
        smooth: true,
        areaStyle: {
          opacity: 0.3,
        },
        lineStyle: {
          color: '#52c41a',
        },
        itemStyle: {
          color: '#52c41a',
        },
      },
    ],
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
  });

  /**
   * 获取状态标签颜色
   */
  const getStatusColor = (status: string) => {
    const colorMap: Record<string, string> = {
      pending: 'default',
      running: 'processing',
      completed: 'success',
      failed: 'error',
      cancelled: 'warning',
    };
    return colorMap[status] || 'default';
  };

  if (!taskId) {
    return (
      <div>
        <Title level={2}>任务监控</Title>
        <Paragraph type="secondary">请选择一个任务进行监控</Paragraph>
        <Alert
          message="未选择任务"
          description="请在订单管理页面点击任务查看监控"
          type="info"
          showIcon
        />
      </div>
    );
  }

  return (
    <Spin spinning={loading}>
      <Title level={2}>任务监控 - {taskId}</Title>

      {/* 任务信息 */}
      {taskStatus && (
        <Card style={{ marginBottom: 24 }}>
          <Descriptions column={4}>
            <Descriptions.Item label="任务ID">{taskId}</Descriptions.Item>
            <Descriptions.Item label="状态">
              <Tag color={getStatusColor(taskStatus.status)}>
                {taskStatus.status}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="开始时间">
              {taskStatus.started_at || taskStatus.start_time || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="预计剩余">
              {taskStatus.estimated_remaining || '-'}
            </Descriptions.Item>
          </Descriptions>
        </Card>
      )}

      {/* 实时指标 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Space>
              <ThunderboltOutlined style={{ fontSize: 32, color: '#1890ff' }} />
              <div>
                <Text type="secondary">实时功率</Text>
                <Title level={3} style={{ margin: 0 }}>
                  {powerData[powerData.length - 1]?.toFixed(2) || '0.00'} kW
                </Title>
              </div>
            </Space>
          </Card>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <Card>
            <Space>
              <CloudOutlined style={{ fontSize: 32, color: '#52c41a' }} />
              <div>
                <Text type="secondary">累计碳排放</Text>
                <Title level={3} style={{ margin: 0 }}>
                  {carbonData.reduce((a: number, b: number) => a + b, 0).toFixed(2) || '0.00'} kg
                </Title>
              </div>
            </Space>
          </Card>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <Card>
            <Space>
              <MoneyCollectOutlined style={{ fontSize: 32, color: '#faad14' }} />
              <div>
                <Text type="secondary">预计总费用</Text>
                <Title level={3} style={{ margin: 0 }}>
                  ¥{taskStatus?.total_cost?.toFixed(2) || '0.00'}
                </Title>
              </div>
            </Space>
          </Card>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <Card>
            <Space>
              <ClockCircleOutlined style={{ fontSize: 32, color: '#722ed1' }} />
              <div>
                <Text type="secondary">运行时长</Text>
                <Title level={3} style={{ margin: 0 }}>
                  {taskStatus?.running_hours || '0'}h
                </Title>
              </div>
            </Space>
          </Card>
        </Col>
      </Row>

      {/* 功耗曲线 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={12}>
          <Card>
            <ReactECharts option={getPowerChartOption()} style={{ height: 300 }} />
          </Card>
        </Col>

        {/* 碳排放曲线 */}
        <Col span={12}>
          <Card>
            <ReactECharts option={getCarbonChartOption()} style={{ height: 300 }} />
          </Card>
        </Col>
      </Row>

      {/* 任务日志 */}
      <Card
        title="任务日志"
        extra={
          <Button
            size="small"
            onClick={() => {
              /* 暂停/继续轮询 */
              if (pollingInterval) {
                clearInterval(pollingInterval);
                setPollingInterval(null);
                message.info('已暂停自动刷新');
              } else if (taskId) {
                startPolling(taskId);
                message.info('已恢复自动刷新');
              }
            }}
          >
            {pollingInterval ? '暂停刷新' : '恢复刷新'}
          </Button>
        }
      >
        <Timeline
          items={logs.map((log) => ({
            children: log,
          }))}
          style={{ height: 300, overflow: 'auto' }}
        />
      </Card>

      {/* 操作按钮 */}
      <Space style={{ marginTop: 16 }}>
        <Button
          icon={<PauseCircleOutlined />}
          disabled={taskStatus?.status !== 'running'}
          onClick={() => {
            message.info('暂停任务功能待实现');
          }}
        >
          暂停任务
        </Button>
        <Button
          icon={<CheckCircleOutlined />}
          disabled={taskStatus?.status !== 'running'}
          onClick={() => {
            message.info('查看详细日志功能待实现');
          }}
        >
          查看详细日志
        </Button>
        <Button
          onClick={() => navigate('/orders')}
        >
          返回订单列表
        </Button>
      </Space>
    </Spin>
  );
};

export default MonitoringPage;
