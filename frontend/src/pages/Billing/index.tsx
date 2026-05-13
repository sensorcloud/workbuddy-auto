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
  Input,
  Select,
  DatePicker,
  Tabs,
  Descriptions,
  message,
  DescriptionsProps,
} from 'antd';
import {
  FileTextOutlined,
  ReloadOutlined,
  PrinterOutlined,
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import dayjs from 'dayjs';
import * as billingService from '@/services/billingService';
import type { MonthlyBill, Invoice, InvoiceCreateRequest, Reconciliation } from '@/types/billing.types';

const { Title, Text, Paragraph } = Typography;
const { RangePicker } = DatePicker;

/**
 * 账单管理页面
 */
const BillingPage: React.FC = () => {
  // 状态
  const [loading, setLoading] = useState(false);
  const [currentBill, setCurrentBill] = useState<MonthlyBill | null>(null);
  const [billList, setBillList] = useState<MonthlyBill[]>([]);
  const [billTotal, setBillTotal] = useState(0);
  const [billPage, setBillPage] = useState(1);
  const [billPageSize, setBillPageSize] = useState(12);

  // 发票相关
  const [invoiceList, setInvoiceList] = useState<Invoice[]>([]);
  const [invoiceTotal, setInvoiceTotal] = useState(0);
  const [invoicePage, setInvoicePage] = useState(1);
  const [invoicePageSize, setInvoicePageSize] = useState(20);
  const [invoiceVisible, setInvoiceVisible] = useState(false);
  const [invoiceLoading, setInvoiceLoading] = useState(false);
  const [invoiceForm] = Form.useForm();

  // 对账相关
  const [reconciliation, setReconciliation] = useState<Reconciliation | null>(null);
  const [reconciliationLoading, setReconciliationLoading] = useState(false);
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs] | null>(null);

  // 月份选择
  const [selectedMonth, setSelectedMonth] = useState(dayjs());

  /**
   * 获取当前月度账单
   */
  const fetchCurrentBill = useCallback(async (year: number, month: number) => {
    setLoading(true);
    try {
      const res = await billingService.getMonthlyBill(year, month);
      setCurrentBill(res.data || null);
    } catch (error) {
      console.error('Failed to fetch current bill:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * 获取账单列表
   */
  const fetchBillList = useCallback(async () => {
    setLoading(true);
    try {
      const res = await billingService.listBills({
        page: billPage,
        page_size: billPageSize,
      });
      setBillList(res.data?.items || []);
      setBillTotal(res.data?.total || 0);
    } catch (error) {
      console.error('Failed to fetch bill list:', error);
      message.error('获取账单列表失败');
    } finally {
      setLoading(false);
    }
  }, [billPage, billPageSize]);

  /**
   * 获取发票列表
   */
  const fetchInvoiceList = useCallback(async () => {
    setLoading(true);
    try {
      const res = await billingService.listInvoices({
        page: invoicePage,
        page_size: invoicePageSize,
      });
      setInvoiceList(res.data?.items || []);
      setInvoiceTotal(res.data?.total || 0);
    } catch (error) {
      console.error('Failed to fetch invoice list:', error);
      message.error('获取发票列表失败');
    } finally {
      setLoading(false);
    }
  }, [invoicePage, invoicePageSize]);

  useEffect(() => {
    fetchCurrentBill(selectedMonth.year(), selectedMonth.month() + 1);
  }, [selectedMonth, fetchCurrentBill]);

  useEffect(() => {
    fetchBillList();
  }, [fetchBillList]);

  /**
   * 查询对账
   */
  const handleReconciliation = async () => {
    if (!dateRange) {
      message.warning('请选择对账日期范围');
      return;
    }
    setReconciliationLoading(true);
    try {
      const res = await billingService.getReconciliation(
        dateRange[0].toISOString(),
        dateRange[1].toISOString()
      );
      setReconciliation(res.data || null);
    } catch (error) {
      console.error('Failed to fetch reconciliation:', error);
      message.error('获取对账信息失败');
    } finally {
      setReconciliationLoading(false);
    }
  };

  /**
   * 申请发票
   */
  const handleCreateInvoice = async () => {
    if (!currentBill) {
      message.warning('请先选择一个账单');
      return;
    }
    try {
      const values = await invoiceForm.validateFields();
      setInvoiceLoading(true);
      await billingService.createInvoice(currentBill.id, values as InvoiceCreateRequest);
      message.success('发票申请已提交');
      setInvoiceVisible(false);
      invoiceForm.resetFields();
      fetchInvoiceList();
    } catch (error: any) {
      if (!error.errorFields) {
        message.error(error?.message || '申请失败');
      }
    } finally {
      setInvoiceLoading(false);
    }
  };

  /**
   * 费用分解饼图
   */
  const getPieChartOption = () => {
    if (!currentBill) return {};
    const data = [
      { name: '算力费', value: currentBill.compute_fee },
      { name: '能源费', value: currentBill.energy_fee },
      { name: '网络费', value: currentBill.network_fee },
      { name: '存储费', value: currentBill.storage_fee },
    ].filter((d) => d.value > 0);

    return {
      title: {
        text: '费用分解',
        left: 'center',
      },
      tooltip: {
        trigger: 'item',
        formatter: '{b}: ¥{c} ({d}%)',
      },
      legend: {
        bottom: 10,
        left: 'center',
      },
      series: [
        {
          type: 'pie',
          radius: '60%',
          data,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)',
            },
          },
        },
      ],
    };
  };

  const billColumns = [
    {
      title: '年月',
      key: 'year_month',
      width: 100,
      render: (_: any, record: MonthlyBill) => `${record.year}-${String(record.month).padStart(2, '0')}`,
    },
    {
      title: '总金额',
      dataIndex: 'total_amount',
      key: 'total_amount',
      width: 120,
      render: (val: number) => `¥${val.toFixed(2)}`,
    },
    {
      title: '算力费',
      dataIndex: 'compute_fee',
      key: 'compute_fee',
      width: 100,
      render: (val: number) => `¥${val.toFixed(2)}`,
    },
    {
      title: '能源费',
      dataIndex: 'energy_fee',
      key: 'energy_fee',
      width: 100,
      render: (val: number) => `¥${val.toFixed(2)}`,
    },
    {
      title: '网络费',
      dataIndex: 'network_fee',
      key: 'network_fee',
      width: 100,
      render: (val: number) => `¥${val.toFixed(2)}`,
    },
    {
      title: '存储费',
      dataIndex: 'storage_fee',
      key: 'storage_fee',
      width: 100,
      render: (val: number) => `¥${val.toFixed(2)}`,
    },
    {
      title: '绿证折扣',
      dataIndex: 'green_cert_discount',
      key: 'green_cert_discount',
      width: 100,
      render: (val: number) => `-¥${Math.abs(val).toFixed(2)}`,
    },
    {
      title: '实付',
      dataIndex: 'actual_pay',
      key: 'actual_pay',
      width: 120,
      render: (val: number) => (
        <Text strong type="success">
          ¥{val.toFixed(2)}
        </Text>
      ),
    },
    {
      title: '订单数',
      dataIndex: 'order_count',
      key: 'order_count',
      width: 80,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 80,
      render: (val: string) => (
        <Tag color={val === 'paid' ? 'green' : 'orange'}>{val}</Tag>
      ),
    },
  ];

  const invoiceColumns = [
    {
      title: '发票ID',
      dataIndex: 'id',
      key: 'id',
      ellipsis: true,
      width: 200,
    },
    {
      title: '账单ID',
      dataIndex: 'bill_id',
      key: 'bill_id',
      ellipsis: true,
      width: 200,
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 80,
      render: (val: string) => (val === 'normal' ? '普通' : '专用'),
    },
    {
      title: '抬头',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
    },
    {
      title: '金额',
      dataIndex: 'amount',
      key: 'amount',
      width: 120,
      render: (val: number) => `¥${val.toFixed(2)}`,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 80,
      render: (val: string) => {
        const colorMap: Record<string, string> = {
          pending: 'orange',
          issued: 'green',
          cancelled: 'red',
        };
        const labelMap: Record<string, string> = {
          pending: '待开',
          issued: '已开',
          cancelled: '已取消',
        };
        return <Tag color={colorMap[val] || 'default'}>{labelMap[val] || val}</Tag>;
      },
    },
    {
      title: '开票时间',
      dataIndex: 'issued_at',
      key: 'issued_at',
      width: 180,
      render: (val?: string) => val || '-',
    },
  ];

  const reconciliationItems: DescriptionsProps['items'] = reconciliation
    ? [
        { key: '1', label: '总订单数', children: reconciliation.total_orders },
        { key: '2', label: '总金额', children: `¥${reconciliation.total_amount.toFixed(2)}` },
        { key: '3', label: '总支付', children: `¥${reconciliation.total_payments.toFixed(2)}` },
        { key: '4', label: '总退款', children: `¥${reconciliation.total_refunds.toFixed(2)}` },
        {
          key: '5',
          label: '差异',
          children: (
            <Text type={reconciliation.discrepancy !== 0 ? 'danger' : 'success'}>
              ¥{reconciliation.discrepancy.toFixed(2)}
            </Text>
          ),
        },
      ]
    : [];

  const tabItems = [
    {
      key: 'bill',
      label: '月度账单',
      children: (
        <>
          {/* 当前月度账单 */}
          <Card style={{ marginBottom: 24 }} loading={loading}>
            <Space style={{ marginBottom: 16 }}>
              <Text>选择月份：</Text>
              <DatePicker
                picker="month"
                value={selectedMonth}
                onChange={(val) => val && setSelectedMonth(val)}
              />
              <Button icon={<ReloadOutlined />} onClick={() => fetchCurrentBill(selectedMonth.year(), selectedMonth.month() + 1)}>
                刷新
              </Button>
            </Space>

            {currentBill && (
              <Row gutter={[16, 16]}>
                <Col xs={24} md={16}>
                  <Descriptions column={2} bordered size="small">
                    <Descriptions.Item label="账单年月">
                      {currentBill.year}年{currentBill.month}月
                    </Descriptions.Item>
                    <Descriptions.Item label="状态">
                      <Tag color={currentBill.status === 'paid' ? 'green' : 'orange'}>
                        {currentBill.status}
                      </Tag>
                    </Descriptions.Item>
                    <Descriptions.Item label="总金额">
                      ¥{currentBill.total_amount.toFixed(2)}
                    </Descriptions.Item>
                    <Descriptions.Item label="实付金额">
                      <Text strong type="success">
                        ¥{currentBill.actual_pay.toFixed(2)}
                      </Text>
                    </Descriptions.Item>
                    <Descriptions.Item label="算力费">
                      ¥{currentBill.compute_fee.toFixed(2)}
                    </Descriptions.Item>
                    <Descriptions.Item label="能源费">
                      ¥{currentBill.energy_fee.toFixed(2)}
                    </Descriptions.Item>
                    <Descriptions.Item label="网络费">
                      ¥{currentBill.network_fee.toFixed(2)}
                    </Descriptions.Item>
                    <Descriptions.Item label="存储费">
                      ¥{currentBill.storage_fee.toFixed(2)}
                    </Descriptions.Item>
                    <Descriptions.Item label="绿证折扣">
                      -¥{Math.abs(currentBill.green_cert_discount).toFixed(2)}
                    </Descriptions.Item>
                    <Descriptions.Item label="订单数">
                      {currentBill.order_count}
                    </Descriptions.Item>
                  </Descriptions>
                  <Button
                    type="primary"
                    icon={<PrinterOutlined />}
                    style={{ marginTop: 16 }}
                    onClick={() => {
                      if (currentBill.status !== 'paid') {
                        message.warning('该账单尚未支付，暂不能申请发票');
                        return;
                      }
                      invoiceForm.setFieldsValue({ type: 'normal' });
                      setInvoiceVisible(true);
                    }}
                  >
                    申请发票
                  </Button>
                </Col>
                <Col xs={24} md={8}>
                  <ReactECharts option={getPieChartOption()} style={{ height: 300 }} />
                </Col>
              </Row>
            )}
          </Card>

          {/* 账单列表 */}
          <Card title="历史账单">
            <Table
              dataSource={billList}
              columns={billColumns}
              rowKey="id"
              loading={loading}
              locale={{ emptyText: '暂无账单记录' }}
              pagination={{
                current: billPage,
                pageSize: billPageSize,
                total: billTotal,
                onChange: (p, ps) => {
                  setBillPage(p);
                  setBillPageSize(ps);
                },
                showSizeChanger: true,
                showTotal: (t) => `共 ${t} 条记录`,
              }}
            />
          </Card>
        </>
      ),
    },
    {
      key: 'invoice',
      label: '发票管理',
      children: (
        <Card>
          <Table
            dataSource={invoiceList}
            columns={invoiceColumns}
            rowKey="id"
            loading={loading}
            locale={{ emptyText: '暂无发票记录' }}
            pagination={{
              current: invoicePage,
              pageSize: invoicePageSize,
              total: invoiceTotal,
              onChange: (p, ps) => {
                setInvoicePage(p);
                setInvoicePageSize(ps);
              },
              showSizeChanger: true,
              showTotal: (t) => `共 ${t} 条记录`,
            }}
          />
        </Card>
      ),
    },
    {
      key: 'reconciliation',
      label: '对账管理',
      children: (
        <Card>
          <Space style={{ marginBottom: 16 }}>
            <Text>选择日期范围：</Text>
            <RangePicker
              value={dateRange}
              onChange={(val) => setDateRange(val as [dayjs.Dayjs, dayjs.Dayjs] | null)}
            />
            <Button
              type="primary"
              onClick={handleReconciliation}
              loading={reconciliationLoading}
            >
              查询
            </Button>
          </Space>

          {reconciliation && (
            <>
              <Descriptions
                title="对账摘要"
                bordered
                column={2}
                items={reconciliationItems}
                style={{ marginBottom: 24 }}
              />
              {reconciliation.details && reconciliation.details.length > 0 && (
                <Table
                  dataSource={reconciliation.details}
                  rowKey={(record: any, index) => String(index)}
                  columns={[
                    {
                      title: '日期',
                      dataIndex: 'date',
                      key: 'date',
                    },
                    {
                      title: '订单数',
                      dataIndex: 'order_count',
                      key: 'order_count',
                    },
                    {
                      title: '金额',
                      dataIndex: 'amount',
                      key: 'amount',
                      render: (val: number) => `¥${val.toFixed(2)}`,
                    },
                  ]}
                  pagination={false}
                />
              )}
            </>
          )}
        </Card>
      ),
    },
  ];

  return (
    <div>
      <Title level={2}>账单管理</Title>
      <Paragraph type="secondary">查看和管理您的账单、发票及对账信息</Paragraph>

      <Tabs items={tabItems} />

      {/* 申请发票 Modal */}
      <Modal
        title="申请发票"
        open={invoiceVisible}
        onCancel={() => setInvoiceVisible(false)}
        onOk={handleCreateInvoice}
        confirmLoading={invoiceLoading}
      >
        <Form form={invoiceForm} layout="vertical">
          <Form.Item
            name="type"
            label="发票类型"
            rules={[{ required: true, message: '请选择发票类型' }]}
          >
            <Select
              options={[
                { label: '普通发票', value: 'normal' },
                { label: '增值税专用发票', value: 'special' },
              ]}
            />
          </Form.Item>
          <Form.Item
            name="title"
            label="发票抬头"
            rules={[{ required: true, message: '请输入发票抬头' }]}
          >
            <Input placeholder="请输入发票抬头" />
          </Form.Item>
          <Form.Item
            name="tax_no"
            label="税号"
            rules={[{ required: true, message: '请输入税号' }]}
          >
            <Input placeholder="请输入税号" />
          </Form.Item>
          <Form.Item name="address" label="地址">
            <Input placeholder="请输入地址（可选）" />
          </Form.Item>
          <Form.Item name="phone" label="电话">
            <Input placeholder="请输入电话（可选）" />
          </Form.Item>
          <Form.Item name="bank_name" label="开户行">
            <Input placeholder="请输入开户行（可选）" />
          </Form.Item>
          <Form.Item name="bank_account" label="银行账号">
            <Input placeholder="请输入银行账号（可选）" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default BillingPage;
