import React, { useState, useEffect, useCallback } from 'react';
import {
  Card,
  Row,
  Col,
  Typography,
  Space,
  Button,
  Table,
  Tag,
  Modal,
  Form,
  InputNumber,
  Select,
  Input,
  message,
  Statistic,
} from 'antd';
import {
  WalletOutlined,
  ReloadOutlined,
  ThunderboltOutlined,
  LockOutlined,
  ShoppingCartOutlined,
} from '@ant-design/icons';
import { apiService } from '@/services/api';
import * as walletService from '@/services/walletService';
import type { WalletBalance, TransactionRecord } from '@/types/wallet.types';

const { Title, Text, Paragraph } = Typography;

/**
 * 钱包管理页面
 */
const WalletPage: React.FC = () => {
  const [balance, setBalance] = useState<WalletBalance | null>(null);
  const [loading, setLoading] = useState(false);
  const [transactions, setTransactions] = useState<TransactionRecord[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [txType, setTxType] = useState<string | undefined>(undefined);

  // Modal 状态
  const [rechargeVisible, setRechargeVisible] = useState(false);
  const [withdrawVisible, setWithdrawVisible] = useState(false);
  const [alertVisible, setAlertVisible] = useState(false);
  const [rechargeLoading, setRechargeLoading] = useState(false);
  const [withdrawLoading, setWithdrawLoading] = useState(false);
  const [alertLoading, setAlertLoading] = useState(false);
  const [rechargeForm] = Form.useForm();
  const [withdrawForm] = Form.useForm();
  const [alertForm] = Form.useForm();

  /**
   * 获取钱包余额
   */
  const fetchBalance = useCallback(async () => {
    setLoading(true);
    try {
      const res = await walletService.getBalance();
      setBalance(res.data || null);
      alertForm.setFieldsValue({ threshold: res.data?.low_balance_alert || 0 });
    } catch (error) {
      console.error('Failed to fetch balance:', error);
      message.error('获取钱包余额失败');
    } finally {
      setLoading(false);
    }
  }, [alertForm]);

  /**
   * 获取交易流水
   */
  const fetchTransactions = useCallback(async () => {
    setLoading(true);
    try {
      const res = await walletService.getTransactions({
        type: txType,
        page,
        page_size: pageSize,
      });
      setTransactions(res.data?.items || []);
      setTotal(res.data?.total || 0);
    } catch (error) {
      console.error('Failed to fetch transactions:', error);
      message.error('获取交易流水失败');
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, txType]);

  useEffect(() => {
    fetchBalance();
  }, [fetchBalance]);

  useEffect(() => {
    fetchTransactions();
  }, [fetchTransactions]);

  /**
   * 充值
   */
  const handleRecharge = async () => {
    try {
      const values = await rechargeForm.validateFields();
      setRechargeLoading(true);
      await walletService.recharge(values);
      message.success('充值成功');
      setRechargeVisible(false);
      rechargeForm.resetFields();
      fetchBalance();
      fetchTransactions();
    } catch (error: any) {
      if (!error.errorFields) {
        message.error(error?.message || '充值失败');
      }
    } finally {
      setRechargeLoading(false);
    }
  };

  /**
   * 提现
   */
  const handleWithdraw = async () => {
    try {
      const values = await withdrawForm.validateFields();
      setWithdrawLoading(true);
      await walletService.withdraw(values);
      message.success('提现申请已提交');
      setWithdrawVisible(false);
      withdrawForm.resetFields();
      fetchBalance();
      fetchTransactions();
    } catch (error: any) {
      if (!error.errorFields) {
        message.error(error?.message || '提现申请失败');
      }
    } finally {
      setWithdrawLoading(false);
    }
  };

  /**
   * 设置低余额告警
   */
  const handleSetAlert = async () => {
    try {
      const values = await alertForm.validateFields();
      setAlertLoading(true);
      await walletService.setLowBalanceAlert(values.threshold);
      message.success('低余额告警设置成功');
      setAlertVisible(false);
      fetchBalance();
    } catch (error: any) {
      if (!error.errorFields) {
        message.error(error?.message || '设置失败');
      }
    } finally {
      setAlertLoading(false);
    }
  };

  /**
   * 交易类型中文映射
   */
  const getTxTypeLabel = (type: string) => {
    const map: Record<string, string> = {
      recharge: '充值',
      freeze: '冻结',
      unfreeze: '解冻',
      consume: '消费',
      refund: '退款',
      withdraw: '提现',
    };
    return map[type] || type;
  };

  /**
   * 交易类型颜色
   */
  const getTxTypeColor = (type: string) => {
    const map: Record<string, string> = {
      recharge: 'green',
      freeze: 'orange',
      unfreeze: 'cyan',
      consume: 'red',
      refund: 'blue',
      withdraw: 'purple',
    };
    return map[type] || 'default';
  };

  const columns = [
    {
      title: '交易ID',
      dataIndex: 'id',
      key: 'id',
      ellipsis: true,
      width: 220,
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 100,
      render: (text: string) => (
        <Tag color={getTxTypeColor(text)}>{getTxTypeLabel(text)}</Tag>
      ),
    },
    {
      title: '金额',
      dataIndex: 'amount',
      key: 'amount',
      width: 120,
      render: (val: number, record: TransactionRecord) => {
        const isPositive = record.type === 'recharge' || record.type === 'refund' || record.type === 'unfreeze';
        return (
          <Text type={isPositive ? 'success' : 'danger'}>
            {isPositive ? '+' : '-'}¥{Math.abs(val).toFixed(2)}
          </Text>
        );
      },
    },
    {
      title: '交易后余额',
      dataIndex: 'balance_after',
      key: 'balance_after',
      width: 120,
      render: (val: number) => `¥${val.toFixed(2)}`,
    },
    {
      title: '关联订单',
      dataIndex: 'order_id',
      key: 'order_id',
      ellipsis: true,
      render: (val?: string) => val || '-',
    },
    {
      title: '备注',
      dataIndex: 'remark',
      key: 'remark',
      ellipsis: true,
      render: (val?: string) => val || '-',
    },
    {
      title: '时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
    },
  ];

  return (
    <div>
      <Title level={2}>钱包管理</Title>
      <Paragraph type="secondary">管理您的账户余额、充值、提现和交易记录</Paragraph>

      {/* 余额统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card loading={loading}>
            <Statistic
              title="账户余额"
              value={balance?.balance || 0}
              precision={2}
              prefix={<WalletOutlined />}
              suffix="元"
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card loading={loading}>
            <Statistic
              title="可用余额"
              value={balance?.available || 0}
              precision={2}
              prefix={<ThunderboltOutlined />}
              suffix="元"
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card loading={loading}>
            <Statistic
              title="冻结金额"
              value={balance?.frozen || 0}
              precision={2}
              prefix={<LockOutlined />}
              suffix="元"
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card loading={loading}>
            <Statistic
              title="累计消费"
              value={balance?.total_consume || 0}
              precision={2}
              prefix={<ShoppingCartOutlined />}
              suffix="元"
              valueStyle={{ color: '#f5222d' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 操作按钮 */}
      <Card style={{ marginBottom: 24 }}>
        <Space wrap>
          <Button type="primary" onClick={() => setRechargeVisible(true)}>
            充值
          </Button>
          <Button onClick={() => setWithdrawVisible(true)}>
            提现
          </Button>
          <Button onClick={() => setAlertVisible(true)}>
            低余额告警设置
          </Button>
          <Button icon={<ReloadOutlined />} onClick={fetchBalance}>
            刷新余额
          </Button>
        </Space>
      </Card>

      {/* 交易流水 */}
      <Card title="交易流水">
        <Space size={16} style={{ marginBottom: 16 }} wrap>
          <Select
            placeholder="交易类型"
            allowClear
            style={{ width: 150 }}
            value={txType}
            onChange={(val) => {
              setTxType(val);
              setPage(1);
            }}
            options={[
              { label: '充值', value: 'recharge' },
              { label: '冻结', value: 'freeze' },
              { label: '解冻', value: 'unfreeze' },
              { label: '消费', value: 'consume' },
              { label: '退款', value: 'refund' },
              { label: '提现', value: 'withdraw' },
            ]}
          />
          <Button icon={<ReloadOutlined />} onClick={fetchTransactions}>
            刷新
          </Button>
        </Space>

        <Table
          dataSource={transactions}
          columns={columns}
          rowKey="id"
          loading={loading}
          locale={{ emptyText: '暂无交易记录' }}
          pagination={{
            current: page,
            pageSize: pageSize,
            total: total,
            onChange: (p, ps) => {
              setPage(p);
              setPageSize(ps);
            },
            showSizeChanger: true,
            showTotal: (t) => `共 ${t} 条记录`,
          }}
        />
      </Card>

      {/* 充值 Modal */}
      <Modal
        title="充值"
        open={rechargeVisible}
        onCancel={() => setRechargeVisible(false)}
        onOk={handleRecharge}
        confirmLoading={rechargeLoading}
      >
        <Form form={rechargeForm} layout="vertical">
          <Form.Item
            name="amount"
            label="充值金额"
            rules={[{ required: true, message: '请输入充值金额' }]}
          >
            <InputNumber
              min={0.01}
              precision={2}
              style={{ width: '100%' }}
              placeholder="请输入充值金额"
              addonAfter="元"
            />
          </Form.Item>
          <Form.Item
            name="channel"
            label="充值渠道"
            initialValue="alipay"
            rules={[{ required: true, message: '请选择充值渠道' }]}
          >
            <Select
              options={[
                { label: '支付宝', value: 'alipay' },
                { label: '微信支付', value: 'wechat' },
                { label: '银行卡', value: 'bankcard' },
              ]}
            />
          </Form.Item>
        </Form>
      </Modal>

      {/* 提现 Modal */}
      <Modal
        title="提现"
        open={withdrawVisible}
        onCancel={() => setWithdrawVisible(false)}
        onOk={handleWithdraw}
        confirmLoading={withdrawLoading}
      >
        <Form form={withdrawForm} layout="vertical">
          <Form.Item
            name="amount"
            label="提现金额"
            rules={[{ required: true, message: '请输入提现金额' }]}
          >
            <InputNumber
              min={0.01}
              precision={2}
              style={{ width: '100%' }}
              placeholder="请输入提现金额"
              addonAfter="元"
            />
          </Form.Item>
          <Form.Item
            name="bank_card"
            label="银行卡号"
            rules={[{ required: true, message: '请输入银行卡号' }]}
          >
            <Input placeholder="请输入银行卡号" />
          </Form.Item>
          <Form.Item
            name="bank_name"
            label="开户行"
            rules={[{ required: true, message: '请输入开户行' }]}
          >
            <Input placeholder="请输入开户行名称" />
          </Form.Item>
          <Form.Item
            name="account_name"
            label="持卡人姓名"
            rules={[{ required: true, message: '请输入持卡人姓名' }]}
          >
            <Input placeholder="请输入持卡人姓名" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 低余额告警设置 Modal */}
      <Modal
        title="低余额告警设置"
        open={alertVisible}
        onCancel={() => setAlertVisible(false)}
        onOk={handleSetAlert}
        confirmLoading={alertLoading}
      >
        <Form form={alertForm} layout="vertical">
          <Form.Item
            name="threshold"
            label="告警阈值（元）"
            extra="当账户余额低于此值时，将收到告警通知"
          >
            <InputNumber
              min={0}
              precision={2}
              style={{ width: '100%' }}
              placeholder="请输入告警阈值"
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default WalletPage;
