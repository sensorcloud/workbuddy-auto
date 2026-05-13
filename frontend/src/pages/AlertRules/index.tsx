import React, { useState, useEffect, useCallback } from 'react';
import {
  Card, Button, Table, Tag, Space, Typography, Modal, Form, Input,
  Select, Switch, Radio, InputNumber, message, Spin, Descriptions, Tooltip
} from 'antd';
import {
  PlusOutlined, EditOutlined, DeleteOutlined, ExclamationCircleOutlined,
  EyeOutlined, SettingOutlined
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import { apiService } from '@/services/api';
import type { AlertRule, Alert } from '@/types/monitoring.types';

const { Title, Text, Paragraph } = Typography;

interface MetricOption { label: string; value: string; }
interface ConditionOption { label: string; value: string; }

const metricOptions: MetricOption[] = [
  { value: 'gpu_util', label: 'GPU利用率' },
  { value: 'gpu_memory', label: 'GPU显存' },
  { value: 'cpu_util', label: 'CPU利用率' },
  { value: 'memory', label: '内存' },
  { value: 'power', label: '功耗' },
  { value: 'temperature', label: '温度' },
  { value: 'pue', label: 'PUE' },
];
const conditionOptions: ConditionOption[] = [
  { value: 'gt', label: '大于' },
  { value: 'lt', label: '小于' },
  { value: 'eq', label: '等于' },
  { value: 'gte', label: '大于等于' },
  { value: 'lte', label: '小于等于' },
];

const metricMap: Record<string, string> = {
  gpu_util: 'GPU利用率',
  gpu_memory: 'GPU显存',
  cpu_util: 'CPU利用率',
  memory: '内存',
  power: '功耗',
  temperature: '温度',
  pue: 'PUE',
};
const conditionMap: Record<string, string> = {
  gt: '大于', lt: '小于', eq: '等于', gte: '大于等于', lte: '小于等于',
};

const AlertRulesPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'rules' | 'history'>('rules');
  const [loading, setLoading] = useState(false);

  // Rules
  const [rules, setRules] = useState<AlertRule[]>([]);
  const [ruleModalVisible, setRuleModalVisible] = useState(false);
  const [editingRule, setEditingRule] = useState<AlertRule | null>(null);
  const [ruleForm] = Form.useForm();

  // History
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [totalAlerts, setTotalAlerts] = useState(0);
  const [alertPage, setAlertPage] = useState(1);
  const [alertPageSize] = useState(20);

  const fetchRules = useCallback(async () => {
    try {
      const response = await apiService.get<AlertRule[]>('/monitoring/alert-rules');
      setRules(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      console.error('Failed to fetch alert rules:', error);
      message.error('获取告警规则失败');
    }
  }, []);

  const fetchAlerts = useCallback(async () => {
    try {
      const response = await apiService.get<{
        items: Alert[]; total: number; page: number; page_size: number;
      }>('/monitoring/alerts', { page: alertPage, page_size: alertPageSize });
      const data = response.data;
      setAlerts(data?.items || []);
      setTotalAlerts(data?.total || 0);
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
      message.error('获取告警历史失败');
    }
  }, [alertPage, alertPageSize]);

  useEffect(() => {
    if (activeTab === 'rules') {
      fetchRules();
    } else {
      fetchAlerts();
    }
  }, [activeTab, fetchRules, fetchAlerts]);

  // Rule CRUD
  const handleAddRule = () => {
    setEditingRule(null);
    ruleForm.resetFields();
    setRuleModalVisible(true);
  };

  const handleEditRule = (rule: AlertRule) => {
    setEditingRule(rule);
    ruleForm.setFieldsValue({
      name: rule.name,
      resource_id: rule.resource_id,
      metric: rule.metric,
      condition: rule.condition,
      threshold: rule.threshold,
      duration_seconds: rule.duration_seconds,
      notify_channels: rule.notify_channels,
      cooldown_seconds: rule.cooldown_seconds,
    });
    setRuleModalVisible(true);
  };

  const handleDeleteRule = async (ruleId: string) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除此告警规则吗？',
      onOk: async () => {
        try {
          await apiService.delete(`/monitoring/alert-rules/${ruleId}`);
          message.success('告警规则已删除');
          fetchRules();
        } catch (error) {
          message.error('删除失败');
        }
      },
    });
  };

  const handleToggleRule = async (rule: AlertRule) => {
    try {
      await apiService.put(`/monitoring/alert-rules/${rule.id}`, {
        is_active: rule.is_active === 1 ? 0 : 1,
      });
      message.success(rule.is_active ? '已禁用' : '已启用');
      fetchRules();
    } catch (error) {
      message.error('操作失败');
    }
  };

  const handleSubmitRule = async () => {
    try {
      const values = await ruleForm.validateFields();
      if (editingRule) {
        await apiService.put(`/monitoring/alert-rules/${editingRule.id}`, values);
        message.success('告警规则已更新');
      } else {
        await apiService.post('/monitoring/alert-rules', values);
        message.success('告警规则已创建');
      }
      setRuleModalVisible(false);
      fetchRules();
    } catch (error) {
      console.error('Failed to submit rule:', error);
      message.error('提交失败');
    }
  };

  const handleResolveAlert = async (alertId: string) => {
    try {
      await apiService.put(`/monitoring/alerts/${alertId}/resolve`, {});
      message.success('告警已解除');
      fetchAlerts();
    } catch (error) {
      message.error('解除失败');
    }
  };

  return (
    <div>
      <Title level={2}>告警规则管理</Title>
      <Paragraph type="secondary">创建和管理资源监控告警规则</Paragraph>

      <Card
        tabList={[
          { key: 'rules', tab: '告警规则' },
          { key: 'history', tab: '告警历史' },
        ]}
        activeTabKey={activeTab}
        onTabChange={(key) => setActiveTab(key as 'rules' | 'history')}
      >
        {activeTab === 'rules' && (
          <>
            <div style={{ marginBottom: 16 }}>
              <Button type="primary" icon={<PlusOutlined />} onClick={handleAddRule}>
                新建规则
              </Button>
            </div>

            <Table
              dataSource={rules}
              rowKey="id"
              locale={{ emptyText: '暂无告警规则' }}
              columns={[
                { title: '名称', dataIndex: 'name', key: 'name' },
                { title: '资源ID', dataIndex: 'resource_id', key: 'resource_id', ellipsis: true, render: (v: string) => v || '-' },
                { title: '指标', dataIndex: 'metric', key: 'metric', width: 100, render: (v: string) => metricMap[v] || v },
                { title: '条件', key: 'condition', width: 100, render: (_: any, record: AlertRule) => <Tag>{conditionMap[record.condition] || record.condition}</Tag> },
                { title: '阈值', dataIndex: 'threshold', key: 'threshold', width: 80, render: (v: number) => v?.toFixed(2) },
                { title: '持续时间', dataIndex: 'duration_seconds', key: 'duration_seconds', width: 100, render: (v: number) => `${v}秒` },
                { title: '通知渠道', dataIndex: 'notify_channels', key: 'notify_channels', width: 100 },
                { title: '状态', key: 'status', width: 80, render: (_: any, record: AlertRule) => <Tag color={record.is_active ? 'success' : 'error'}>{record.is_active ? '启用' : '禁用'}</Tag> },
                { title: '最后触发', dataIndex: 'last_triggered_at', key: 'last_triggered_at', width: 180, render: (v?: string) => v || '从未' },
                {
                  title: '操作',
                  key: 'action',
                  width: 220,
                  render: (_: any, record: AlertRule) => (
                    <Space>
                      <Button size="small" onClick={() => handleEditRule(record)} icon={<EditOutlined />}>编辑</Button>
                      <Button size="small" onClick={() => handleToggleRule(record)}>{record.is_active ? '禁用' : '启用'}</Button>
                      <Button size="small" danger onClick={() => handleDeleteRule(record.id)} icon={<DeleteOutlined />}>删除</Button>
                    </Space>
                  ),
                },
              ]}
            />
          </>
        )}

        {activeTab === 'history' && (
          <Table
            dataSource={alerts}
            rowKey="id"
            locale={{ emptyText: '暂无告警记录' }}
            columns={[
              { title: '资源ID', dataIndex: 'resource_id', key: 'resource_id', ellipsis: true },
              { title: '指标', dataIndex: 'metric', key: 'metric', render: (v: string) => metricMap[v] || v },
              { title: '当前值', dataIndex: 'value', key: 'value', render: (v: number) => v?.toFixed(2) },
              { title: '阈值', dataIndex: 'threshold', key: 'threshold', render: (v: number) => v?.toFixed(2) },
              { title: '条件', key: 'condition', render: (_: any, record: Alert) => <Tag>{conditionMap[record.condition] || record.condition}</Tag> },
              { title: '状态', key: 'status', render: (_: any, record: Alert) => <Tag color={record.status === 'resolved' ? 'success' : 'error'}>{record.status}</Tag> },
              { title: '消息', dataIndex: 'message', key: 'message', ellipsis: true },
              { title: '时间', dataIndex: 'created_at', key: 'created_at', width: 180 },
              {
                title: '操作',
                key: 'action',
                width: 100,
                render: (_: any, record: Alert) => (
                  record.status !== 'resolved' && (
                    <Button size="small" onClick={() => handleResolveAlert(record.id)}>解除</Button>
                  )
                ),
              },
            ]}
          />
        )}
      </Card>

      {/* Rule Modal */}
      <Modal
        title={editingRule ? '编辑告警规则' : '新建告警规则'}
        open={ruleModalVisible}
        onOk={handleSubmitRule}
        onCancel={() => setRuleModalVisible(false)}
        width={600}
      >
        <Form form={ruleForm} layout="vertical">
          <Form.Item
            name="name"
            label="规则名称"
            rules={[{ required: true, message: '请输入规则名称' }]}
          >
            <Input placeholder="例如：GPU利用率过高告警" />
          </Form.Item>

          <Form.Item
            name="resource_id"
            label="资源ID"
          >
            <Input placeholder="留空表示对所有资源生效" />
          </Form.Item>

          <Form.Item
            name="metric"
            label="监控指标"
            rules={[{ required: true, message: '请选择监控指标' }]}
          >
            <Select options={metricOptions} placeholder="选择监控指标" />
          </Form.Item>

          <Form.Item
            name="condition"
            label="触发条件"
            rules={[{ required: true, message: '请选择触发条件' }]}
          >
            <Select options={conditionOptions} placeholder="选择触发条件" />
          </Form.Item>

          <Form.Item
            name="threshold"
            label="阈值"
            rules={[{ required: true, message: '请输入阈值' }]}
          >
            <InputNumber style={{ width: '100%' }} placeholder="阈值数值" />
          </Form.Item>

          <Form.Item
            name="duration_seconds"
            label="持续时间（秒）"
            initialValue={0}
          >
            <InputNumber style={{ width: '100%' }} min={0} placeholder="0表示立即触发" />
          </Form.Item>

          <Form.Item
            name="notify_channels"
            label="通知渠道"
            initialValue="web"
          >
            <Select placeholder="选择通知渠道">
              <Select.Option value="web">Web</Select.Option>
              <Select.Option value="email">邮件</Select.Option>
              <Select.Option value="sms">短信</Select.Option>
              <Select.Option value="webhook">Webhook</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="cooldown_seconds"
            label="冷却时间（秒）"
            initialValue={300}
          >
            <InputNumber style={{ width: '100%' }} min={0} placeholder="默认300秒" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default AlertRulesPage;
