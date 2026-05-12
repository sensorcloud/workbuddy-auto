import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Typography,
  Tag,
  Modal,
  Form,
  Input,
  InputNumber,
  Select,
  message,
  Popconfirm,
  Empty,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  DollarOutlined,
} from '@ant-design/icons';
import { apiService } from '@/services/api';
import { useAuthStore } from '@/store/authStore';
import type { Asset } from '@/types/asset.types';

const { Title, Text, Paragraph } = Typography;

/**
 * 资产管理页面
 * 提供者视角的资产管理后台，纯API调用
 */
const AssetManagementPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [modalVisible, setModalVisible] = useState(false);
  const [modalType, setModalType] = useState<'compute' | 'storage'>('compute');
  const [editingAsset, setEditingAsset] = useState<Asset | null>(null);
  const [earnings, setEarnings] = useState({ today: 0, thisMonth: 0 });

  const [form] = Form.useForm();
  const authStore = useAuthStore();

  /**
   * 获取资产列表
   */
  const fetchAssets = async () => {
    setLoading(true);

    try {
      const response = await apiService.get<{ items: Asset[]; total: number }>(
        '/assets',
        { page, page_size: pageSize }
      );
      const data = response.data;
      setAssets(data?.items || []);
      setTotal(data?.total || 0);
    } catch (error) {
      console.error('Failed to fetch assets:', error);
      message.error('获取资产列表失败');
    } finally {
      setLoading(false);
    }
  };

  /**
   * 获取收益概览
   */
  const fetchEarnings = async () => {
    try {
      const response = await apiService.get<{
        today: number;
        this_month: number;
        total: number;
      }>('/earnings/summary');
      setEarnings({
        today: response.data?.today || 0,
        thisMonth: response.data?.this_month || 0,
      });
    } catch (error) {
      // 收益接口可能返回空，不影响主流程
      console.log('Earnings not available');
    }
  };

  useEffect(() => {
    fetchAssets();
    fetchEarnings();
  }, [page, pageSize]);

  /**
   * 打开注册/编辑模态框
   */
  const handleOpenModal = (type: 'compute' | 'storage', asset?: Asset) => {
    setModalType(type);
    setEditingAsset(asset || null);

    if (asset) {
      form.setFieldsValue({
        gpu_model: asset.spec?.gpu,
        vram: asset.spec?.vram,
        compute_price_per_hour: asset.pricing?.compute_price_per_hour,
        is_spot: asset.pricing?.is_spot,
        spot_discount: asset.pricing?.spot_discount,
        power_source: asset.energy_profile?.power_source,
        price_per_kwh: asset.energy_profile?.price_per_kwh,
        pue: asset.energy_profile?.PUE,
        region: asset.location?.region,
        zone: asset.location?.zone,
        status: asset.status,
      });
    } else {
      form.resetFields();
    }

    setModalVisible(true);
  };

  /**
   * 提交资产注册/更新
   */
  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      const userId = authStore.user?.id || 'unknown';

      if (editingAsset) {
        // 更新资产
        await apiService.put(`/assets/${editingAsset.id}`, {
          owner_id: userId,
          type: editingAsset.type,
          spec: {
            gpu: values.gpu_model,
            vram: values.vram,
            cpu_cores: values.cpu_cores,
            memory_gb: values.memory_gb,
          },
          energy_profile: {
            price_per_kwh: values.price_per_kwh,
            power_source: values.power_source,
            PUE: values.pue,
          },
          pricing: {
            compute_price_per_hour: values.compute_price_per_hour,
            is_spot: values.is_spot || false,
            spot_discount: values.spot_discount || 0,
          },
          location: {
            region: values.region,
            zone: values.zone,
          },
        });
        message.success('资产更新成功');
      } else {
        // 注册资产
        await apiService.post('/assets', {
          owner_id: userId,
          type: modalType,
          spec: {
            gpu: values.gpu_model,
            vram: values.vram,
            cpu_cores: values.cpu_cores,
            memory_gb: values.memory_gb,
          },
          energy_profile: {
            price_per_kwh: values.price_per_kwh,
            power_source: values.power_source,
            PUE: values.pue,
          },
          pricing: {
            compute_price_per_hour: values.compute_price_per_hour,
            is_spot: values.is_spot || false,
            spot_discount: values.spot_discount || 0,
          },
          location: {
            region: values.region,
            zone: values.zone,
          },
        });
        message.success('资产注册成功，等待审核');
      }

      setModalVisible(false);
      fetchAssets();
    } catch (error: any) {
      if (error.errorFields) return; // 表单验证错误
      message.error(error?.message || '操作失败');
    }
  };

  /**
   * 删除资产
   */
  const handleDelete = async (assetId: string) => {
    try {
      await apiService.delete(`/assets/${assetId}`);
      message.success('资产删除成功');
      fetchAssets();
    } catch (error: any) {
      message.error(error?.message || '删除失败');
    }
  };

  /**
   * 表格列定义
   */
  const columns = [
    {
      title: '资产ID',
      dataIndex: 'id',
      key: 'id',
      ellipsis: true,
      width: 220,
    },
    {
      title: '类型',
      key: 'type',
      width: 100,
      render: (_: any, record: Asset) => (
        <Tag color={record.type === 'compute' ? 'blue' : 'green'}>
          {record.type === 'compute' ? '算力' : record.type === 'storage' ? '储能' : record.type}
        </Tag>
      ),
    },
    {
      title: '规格',
      key: 'spec',
      width: 200,
      render: (_: any, record: Asset) => (
        <Space direction="vertical" size={0}>
          <Text>{record.spec?.gpu || '-'}</Text>
          <Text type="secondary">{record.spec?.vram || '-'}</Text>
        </Space>
      ),
    },
    {
      title: '状态',
      key: 'status',
      width: 100,
      render: (_: any, record: Asset) => {
        const statusMap: Record<string, { color: string; text: string }> = {
          pending: { color: 'default', text: '审核中' },
          online: { color: 'success', text: '在线' },
          offline: { color: 'default', text: '离线' },
          maintenance: { color: 'warning', text: '维护中' },
        };
        const config = statusMap[record.status] || statusMap.pending;
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
    {
      title: '价格',
      key: 'price',
      width: 120,
      render: (_: any, record: Asset) => (
        <Text strong>¥{record.pricing?.compute_price_per_hour?.toFixed(2) || '0.00'}/h</Text>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_: any, record: Asset) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => handleOpenModal(record.type as 'compute' | 'storage', record)}
          >
            详情
          </Button>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleOpenModal(record.type as 'compute' | 'storage', record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定删除此资产？"
            onConfirm={() => handleDelete(record.id)}
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Title level={2}>资产管理</Title>
      <Paragraph type="secondary">
        管理您的算力和能源资产
      </Paragraph>

      {/* 资产概览 */}
      <Card style={{ marginBottom: 24 }}>
        <Space size={32}>
          <div>
            <Text type="secondary">今日收益</Text>
            <Title level={3} style={{ margin: 0, color: '#1890ff' }}>
              ¥{earnings.today.toFixed(2)}
            </Title>
          </div>
          <div>
            <Text type="secondary">本月收益</Text>
            <Title level={3} style={{ margin: 0, color: '#52c41a' }}>
              ¥{earnings.thisMonth.toFixed(2)}
            </Title>
          </div>
          <div>
            <Text type="secondary">资产总数</Text>
            <Title level={3} style={{ margin: 0 }}>
              {total}
            </Title>
          </div>
        </Space>
      </Card>

      {/* 资产列表 */}
      <Card
        title="资产列表"
        extra={
          <Space>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => handleOpenModal('compute')}
            >
              注册算力资产
            </Button>
            <Button
              icon={<DollarOutlined />}
              onClick={() => handleOpenModal('storage')}
            >
              注册储能资产
            </Button>
          </Space>
        }
      >
        <Table
          dataSource={assets}
          columns={columns}
          rowKey="id"
          loading={loading}
          locale={{ emptyText: <Empty description="暂无资产，点击上方按钮注册" /> }}
          pagination={{
            current: page,
            pageSize,
            total,
            onChange: (p, ps) => { setPage(p); setPageSize(ps); },
            showTotal: (t) => `共 ${t} 个资产`,
          }}
        />
      </Card>

      {/* 注册/编辑模态框 */}
      <Modal
        title={editingAsset ? '编辑资产' : `注册${modalType === 'compute' ? '算力' : '储能'}资产`}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={handleSubmit}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          style={{ marginTop: 16 }}
        >
          <Form.Item
            label="GPU型号"
            name="gpu_model"
            rules={[{ required: modalType === 'compute', message: '请输入GPU型号' }]}
          >
            <Input placeholder="例如：A100-80G" />
          </Form.Item>

          <Form.Item
            label="显存"
            name="vram"
            rules={[{ required: modalType === 'compute' }]}
          >
            <Input placeholder="例如：80GB" />
          </Form.Item>

          <Form.Item
            label="CPU核心数"
            name="cpu_cores"
          >
            <InputNumber min={1} style={{ width: '100%' }} placeholder="例如：128" />
          </Form.Item>

          <Form.Item
            label="内存(GB)"
            name="memory_gb"
          >
            <InputNumber min={1} style={{ width: '100%' }} placeholder="例如：512" />
          </Form.Item>

          <Form.Item
            label="电价（¥/kWh）"
            name="price_per_kwh"
            rules={[{ required: true }]}
          >
            <InputNumber min={0} step={0.01} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            label="算力单价（¥/小时）"
            name="compute_price_per_hour"
            rules={[{ required: true }]}
          >
            <InputNumber min={0} step={0.01} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            label="能源来源"
            name="power_source"
            rules={[{ required: true }]}
          >
            <Select
              options={[
                { label: '电网', value: 'grid' },
                { label: '光伏', value: 'solar' },
                { label: '风电', value: 'wind' },
                { label: '储能', value: 'storage' },
              ]}
            />
          </Form.Item>

          <Form.Item
            label="PUE"
            name="pue"
          >
            <InputNumber min={1} max={3} step={0.01} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            label="所在区域"
            name="region"
            rules={[{ required: true }]}
          >
            <Select
              options={[
                { label: '华东', value: 'east-china' },
                { label: '华北', value: 'north-china' },
                { label: '华南', value: 'south-china' },
              ]}
            />
          </Form.Item>

          <Form.Item
            label="可用区"
            name="zone"
          >
            <Input placeholder="例如：zone-a" />
          </Form.Item>

          <Form.Item
            label="是否竞价"
            name="is_spot"
            valuePropName="checked"
          >
            <Select
              options={[
                { label: '标准', value: false },
                { label: '竞价', value: true },
              ]}
            />
          </Form.Item>

          <Form.Item
            label="竞价折扣(0-1)"
            name="spot_discount"
          >
            <InputNumber min={0} max={1} step={0.1} style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default AssetManagementPage;
