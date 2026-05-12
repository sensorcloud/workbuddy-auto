import React, { useState, useEffect, useCallback } from 'react';
import {
  Card,
  Table,
  Tag,
  Space,
  Typography,
  Button,
  Select,
  message,
  Descriptions,
  Modal,
  Popconfirm,
} from 'antd';
import {
  EyeOutlined,
  DeleteOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { apiService } from '@/services/api';
import type { Order, OrderStatus } from '@/types/order.types';

const { Title, Text, Paragraph } = Typography;

/**
 * 订单管理页面
 * 纯API调用，无mock数据
 */
const OrdersPage: React.FC = () => {
  const navigate = useNavigate();

  const [loading, setLoading] = useState(false);
  const [orders, setOrders] = useState<Order[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [statusFilter, setStatusFilter] = useState<string | undefined>(undefined);
  const [detailVisible, setDetailVisible] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);

  /**
   * 获取订单列表
   */
  const fetchOrders = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, any> = {
        page,
        page_size: pageSize,
      };
      if (statusFilter) {
        params.status = statusFilter;
      }

      const response = await apiService.get<{
        items: Order[];
        total: number;
      }>('/orders', params);

      const data = response.data;
      setOrders(data?.items || []);
      setTotal(data?.total || 0);
    } catch (error) {
      console.error('Failed to fetch orders:', error);
      message.error('获取订单列表失败');
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, statusFilter]);

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  /**
   * 查看订单详情
   */
  const handleViewDetail = async (order: Order) => {
    try {
      const response = await apiService.get<Order>(`/orders/${order.id}`);
      setSelectedOrder(response.data || order);
    } catch (error) {
      setSelectedOrder(order);
    } finally {
      setDetailVisible(true);
    }
  };

  /**
   * 取消订单
   */
  const handleCancelOrder = async (orderId: string) => {
    try {
      await apiService.put(`/orders/${orderId}/cancel`, {});
      message.success('订单已取消');
      fetchOrders();
    } catch (error: any) {
      message.error(error?.message || '取消失败');
    }
  };

  /**
   * 获取状态标签颜色
   */
  const getStatusColor = (status: string) => {
    const colorMap: Record<string, string> = {
      pending: 'default',
      paid: 'processing',
      running: 'processing',
      completed: 'success',
      failed: 'error',
      cancelled: 'warning',
    };
    return colorMap[status] || 'default';
  };

  /**
   * 获取任务类型中文
   */
  const getTaskTypeLabel = (taskType?: string) => {
    const map: Record<string, string> = {
      inference: '推理',
      training: '训练',
      render: '渲染',
    };
    return map[taskType || ''] || taskType || '-';
  };

  /**
   * 获取策略中文
   */
  const getStrategyLabel = (strategy?: string) => {
    const map: Record<string, string> = {
      cheapest: '省钱',
      fastest: '快速',
      greenest: '绿色',
      custom: '自定义',
    };
    return map[strategy || ''] || strategy || '-';
  };

  /**
   * 表格列定义
   */
  const columns = [
    {
      title: '订单ID',
      dataIndex: 'id',
      key: 'id',
      ellipsis: true,
      width: 220,
    },
    {
      title: '任务类型',
      dataIndex: 'task_type',
      key: 'task_type',
      width: 100,
      render: (text: string) => getTaskTypeLabel(text),
    },
    {
      title: '策略',
      dataIndex: 'strategy',
      key: 'strategy',
      width: 100,
      render: (text: string) => getStrategyLabel(text),
    },
    {
      title: '状态',
      key: 'status',
      width: 100,
      render: (_: any, record: Order) => (
        <Tag color={getStatusColor(record.status)}>
          {record.status}
        </Tag>
      ),
    },
    {
      title: '预估时长',
      dataIndex: 'estimated_duration_hours',
      key: 'duration',
      width: 100,
      render: (text: number) => `${text || 0}小时`,
    },
    {
      title: '总费用',
      key: 'total_cost',
      width: 120,
      render: (_: any, record: Order) => (
        <Text strong>¥{record.total_cost?.toFixed(2) || '0.00'}</Text>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_: any, record: Order) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => handleViewDetail(record)}
          >
            详情
          </Button>
          {record.status === 'pending' && (
            <Popconfirm
              title="确定取消此订单？"
              onConfirm={() => handleCancelOrder(record.id)}
            >
              <Button type="link" danger>
                取消
              </Button>
            </Popconfirm>
          )}
          {record.status === 'paid' && (
            <Button
              type="link"
              onClick={() => navigate(`/monitoring/${record.id}`)}
            >
              监控
            </Button>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Title level={2}>订单管理</Title>
      <Paragraph type="secondary">
        查看和管理您的订单
      </Paragraph>

      {/* 筛选区域 */}
      <Card style={{ marginBottom: 24 }}>
        <Space size={16} wrap>
          <Select
            placeholder="订单状态"
            allowClear
            style={{ width: 150 }}
            value={statusFilter}
            onChange={(value) => {
              setStatusFilter(value);
              setPage(1);
            }}
            options={[
              { label: '待支付', value: 'pending' },
              { label: '已支付', value: 'paid' },
              { label: '运行中', value: 'running' },
              { label: '已完成', value: 'completed' },
              { label: '已取消', value: 'cancelled' },
            ]}
          />

          <Button
            icon={<ReloadOutlined />}
            onClick={fetchOrders}
          >
            刷新
          </Button>
        </Space>
      </Card>

      {/* 订单列表 */}
      <Card>
        <Table
          dataSource={orders}
          columns={columns}
          rowKey="id"
          loading={loading}
          locale={{ emptyText: '暂无订单' }}
          pagination={{
            current: page,
            pageSize: pageSize,
            total: total,
            onChange: (p, ps) => {
              setPage(p);
              setPageSize(ps);
            },
            showSizeChanger: true,
            showTotal: (t) => `共 ${t} 个订单`,
          }}
        />
      </Card>

      {/* 订单详情模态框 */}
      <Modal
        title="订单详情"
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        footer={null}
        width={800}
      >
        {selectedOrder && (
          <Descriptions column={2} bordered>
            <Descriptions.Item label="订单ID" span={2}>
              {selectedOrder.id}
            </Descriptions.Item>
            <Descriptions.Item label="任务类型">
              {getTaskTypeLabel(selectedOrder.task_type)}
            </Descriptions.Item>
            <Descriptions.Item label="策略">
              <Tag>{getStrategyLabel(selectedOrder.strategy)}</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="状态">
              <Tag color={getStatusColor(selectedOrder.status)}>
                {selectedOrder.status}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="预估时长">
              {selectedOrder.estimated_duration_hours || 0} 小时
            </Descriptions.Item>
            <Descriptions.Item label="创建时间" span={2}>
              {selectedOrder.created_at}
            </Descriptions.Item>
            {selectedOrder.selected_quote && (
              <>
                <Descriptions.Item label="算力成本">
                  ¥{selectedOrder.selected_quote.compute_cost?.toFixed(2)}
                </Descriptions.Item>
                <Descriptions.Item label="能源成本">
                  ¥{selectedOrder.selected_quote.energy_cost?.toFixed(2)}
                </Descriptions.Item>
                <Descriptions.Item label="总费用">
                  <Text strong>¥{selectedOrder.selected_quote.total_cost?.toFixed(2)}</Text>
                </Descriptions.Item>
              </>
            )}
          </Descriptions>
        )}
      </Modal>
    </div>
  );
};

export default OrdersPage;
