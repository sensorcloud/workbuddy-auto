import React, { useState, useEffect, useCallback } from 'react';
import {
  Card,
  Row,
  Col,
  Input,
  Select,
  Slider,
  Tag,
  Button,
  Typography,
  Space,
  Pagination,
  Empty,
  Spin,
  Tooltip,
  Badge,
  message,
} from 'antd';
import {
  SearchOutlined,
  FilterOutlined,
  ThunderboltOutlined,
  EnvironmentOutlined,
  ClockCircleOutlined,
  FireOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { apiService } from '@/services/api';
import type { Asset } from '@/types/asset.types';

const { Title, Text, Paragraph } = Typography;
const { Search } = Input;

/**
 * 资源市场首页
 * 展示可用算力/能源资源，支持多维度筛选
 */
const MarketplacePage: React.FC = () => {
  const navigate = useNavigate();

  // 状态管理
  const [loading, setLoading] = useState(false);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);

  // 筛选条件
  const [filters, setFilters] = useState({
    gpu_model: undefined as string | undefined,
    max_price: undefined as number | undefined,
    power_source: undefined as string | undefined,
    region: undefined as string | undefined,
  });

  /**
   * 获取资源列表
   */
  const fetchAssets = useCallback(async () => {
    setLoading(true);

    try {
      const params: Record<string, any> = {
        page,
        page_size: pageSize,
        status: 'online',
      };

      // 只添加有值的筛选参数
      if (filters.gpu_model) params.gpu_model = filters.gpu_model;
      if (filters.max_price) params.max_price = filters.max_price;
      if (filters.power_source) params.power_source = filters.power_source;
      if (filters.region) params.region = filters.region;

      const response = await apiService.get<{
        items: Asset[];
        total: number;
      }>('/marketplace/assets', params);

      const data = response.data;
      setAssets(data?.items || []);
      setTotal(data?.total || 0);
    } catch (error) {
      console.error('Failed to fetch assets:', error);
      message.error('获取资源列表失败');
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, filters]);

  // 初始加载和筛选条件变化时重新获取
  useEffect(() => {
    fetchAssets();
  }, [fetchAssets]);

  /**
   * 处理搜索
   */
  const handleSearch = (value: string) => {
    setFilters((prev) => ({ ...prev, gpu_model: value || undefined }));
    setPage(1);
  };

  /**
   * 处理筛选条件变化
   */
  const handleFilterChange = (key: string, value: any) => {
    setFilters((prev) => ({ ...prev, [key]: value || undefined }));
    setPage(1);
  };

  /**
   * 重置筛选条件
   */
  const handleResetFilters = () => {
    setFilters({
      gpu_model: undefined,
      max_price: undefined,
      power_source: undefined,
      region: undefined,
    });
    setPage(1);
  };

  /**
   * 查看资源详情
   */
  const handleViewDetail = (assetId: string) => {
    navigate(`/marketplace/${assetId}`);
  };

  /**
   * 立即购买 - 跳转到调度页面
   */
  const handleQuickBuy = (asset: Asset) => {
    navigate('/scheduling');
  };

  /**
   * 获取能源来源中文标签
   */
  const getPowerSourceLabel = (source?: string) => {
    const map: Record<string, string> = {
      solar: '光伏',
      wind: '风电',
      grid: '电网',
      storage: '储能',
    };
    return map[source || ''] || source || '';
  };

  /**
   * 渲染资源卡片
   */
  const renderAssetCard = (asset: Asset) => {
    const isSpot = asset.pricing?.is_spot;
    const discount = asset.pricing?.spot_discount || 0;

    return (
      <Badge.Ribbon
        text={isSpot ? `竞价 ${discount * 100}%OFF` : null}
        color="red"
        style={{ display: isSpot ? 'block' : 'none' }}
      >
        <Card
          hoverable
          style={{ height: '100%' }}
          cover={
            <div
              style={{
                height: 160,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <ThunderboltOutlined style={{ fontSize: 64, color: '#fff' }} />
            </div>
          }
          actions={[
            <Tooltip title="查看详情" key="detail">
              <Button
                type="link"
                onClick={() => handleViewDetail(asset.id)}
              >
                详情
              </Button>
            </Tooltip>,
            <Button
              type="primary"
              key="buy"
              onClick={() => handleQuickBuy(asset)}
            >
              立即购买
            </Button>,
          ]}
        >
          {/* 资源名称 */}
          <Title level={5} style={{ marginBottom: 8 }}>
            {asset.spec?.gpu || 'Unknown GPU'} {isSpot ? '竞价实例' : '标准实例'}
          </Title>

          {/* 价格 */}
          <Space style={{ marginBottom: 12 }}>
            <Text strong style={{ fontSize: 20, color: '#f5222d' }}>
              ¥{asset.pricing?.compute_price_per_hour?.toFixed(2) || '0.00'}
            </Text>
            <Text type="secondary">/小时</Text>
          </Space>

          {/* 标签 */}
          <Space wrap style={{ marginBottom: 12 }}>
            {asset.energy_profile?.power_source && (
              <Tag color="green">
                <FireOutlined /> {getPowerSourceLabel(asset.energy_profile.power_source)}
              </Tag>
            )}
            {asset.location?.region && (
              <Tag color="blue">
                <EnvironmentOutlined /> {asset.location.region}
              </Tag>
            )}
            {asset.status === 'online' && (
              <Tag color="success">在线</Tag>
            )}
          </Space>

          {/* 规格信息 */}
          <Space direction="vertical" size={4} style={{ width: '100%' }}>
            <Space size={16}>
              <Text type="secondary">显存:</Text>
              <Text>{asset.spec?.vram || '-'}</Text>
            </Space>
            <Space size={16}>
              <Text type="secondary">PUE:</Text>
              <Text>{asset.energy_profile?.PUE || '-'}</Text>
            </Space>
            {isSpot && (
              <Space size={16}>
                <Text type="secondary">中断率:</Text>
                <Text type="warning">中</Text>
              </Space>
            )}
          </Space>
        </Card>
      </Badge.Ribbon>
    );
  };

  return (
    <div>
      <Title level={2}>资源市场</Title>
      <Paragraph type="secondary">
        浏览和搜索可用的算力与能源资源
      </Paragraph>

      {/* 筛选区域 */}
      <Card style={{ marginBottom: 24 }}>
        <Row gutter={[16, 16]}>
          {/* 搜索框 */}
          <Col span={24}>
            <Search
              placeholder="搜索GPU型号、数据中心..."
              allowClear
              onSearch={handleSearch}
              style={{ maxWidth: 400 }}
            />
          </Col>

          {/* GPU型号筛选 */}
          <Col xs={24} sm={12} md={6}>
            <Text type="secondary">GPU型号</Text>
            <Select
              placeholder="全部"
              allowClear
              style={{ width: '100%', marginTop: 4 }}
              value={filters.gpu_model}
              onChange={(value) => handleFilterChange('gpu_model', value)}
              options={[
                { label: 'A100 80GB', value: 'A100' },
                { label: 'H100 80GB', value: 'H100' },
                { label: 'L40S', value: 'L40S' },
                { label: 'V100 32GB', value: 'V100' },
              ]}
            />
          </Col>

          {/* 价格区间 */}
          <Col xs={24} sm={12} md={6}>
            <Text type="secondary">价格区间（¥/小时）</Text>
            <Slider
              range
              min={0}
              max={50}
              step={0.5}
              value={filters.max_price ? [0, filters.max_price] : [0, 50]}
              onChange={(value) => handleFilterChange('max_price', value[1])}
              style={{ marginTop: 4 }}
            />
          </Col>

          {/* 能源类型 */}
          <Col xs={24} sm={12} md={6}>
            <Text type="secondary">能源类型</Text>
            <Select
              placeholder="全部"
              allowClear
              style={{ width: '100%', marginTop: 4 }}
              value={filters.power_source}
              onChange={(value) => handleFilterChange('power_source', value)}
              options={[
                { label: '光伏发电', value: 'solar' },
                { label: '风力发电', value: 'wind' },
                { label: '电网供电', value: 'grid' },
                { label: '储能供电', value: 'storage' },
              ]}
            />
          </Col>

          {/* 可用区 */}
          <Col xs={24} sm={12} md={6}>
            <Text type="secondary">可用区</Text>
            <Select
              placeholder="全部"
              allowClear
              style={{ width: '100%', marginTop: 4 }}
              value={filters.region}
              onChange={(value) => handleFilterChange('region', value)}
              options={[
                { label: '华东', value: 'east-china' },
                { label: '华北', value: 'north-china' },
                { label: '华南', value: 'south-china' },
              ]}
            />
          </Col>

          {/* 操作按钮 */}
          <Col span={24} style={{ textAlign: 'right' }}>
            <Space>
              <Button onClick={handleResetFilters}>重置筛选</Button>
              <Button
                type="primary"
                icon={<FilterOutlined />}
                onClick={fetchAssets}
              >
                应用筛选
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 资源列表 */}
      <Spin spinning={loading}>
        {assets.length === 0 && !loading ? (
          <Empty
            description="暂无符合条件的资源"
            style={{ marginTop: 100 }}
          />
        ) : (
          <Row gutter={[16, 16]}>
            {assets.map((asset) => (
              <Col xs={24} sm={12} md={8} lg={6} key={asset.id}>
                {renderAssetCard(asset)}
              </Col>
            ))}
          </Row>
        )}
      </Spin>

      {/* 分页 */}
      <Pagination
        current={page}
        pageSize={pageSize}
        total={total}
        onChange={(p, ps) => {
          setPage(p);
          setPageSize(ps);
        }}
        showSizeChanger
        showQuickJumper
        showTotal={(t) => `共 ${t} 个资源`}
        style={{ marginTop: 24, textAlign: 'center' }}
      />
    </div>
  );
};

export default MarketplacePage;
