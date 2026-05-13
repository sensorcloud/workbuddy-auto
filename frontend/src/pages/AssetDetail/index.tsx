import React, { useState, useEffect } from 'react';
import {
  Card, Button, Typography, Space, Tag, Descriptions, Table, Spin, Row, Col,
  message, Rate, Divider, Empty
} from 'antd';
import {
  ThunderboltOutlined, EnvironmentOutlined, FireOutlined,
  ArrowLeftOutlined, ShoppingCartOutlined
} from '@ant-design/icons';
import { useParams, useNavigate } from 'react-router-dom';
import { apiService } from '@/services/api';
import type { Asset } from '@/types/asset.types';

const { Title, Text, Paragraph } = Typography;

/**
 * 资产详情页面
 * 展示单个算力/能源资源的详细信息
 */
const AssetDetailPage: React.FC = () => {
  const { assetId } = useParams<{ assetId: string }>();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(false);
  const [asset, setAsset] = useState<Asset | null>(null);
  const [reviews, setReviews] = useState<any[]>([]);
  const [reviewTotal, setReviewTotal] = useState(0);

  /**
   * 获取资产详情
   */
  const fetchAssetDetail = async () => {
    if (!assetId) return;
    setLoading(true);
    try {
      const response = await apiService.get<Asset>(`/marketplace/assets/${assetId}`);
      setAsset(response.data);
    } catch (error) {
      console.error('Failed to fetch asset detail:', error);
      message.error('获取资产详情失败');
    } finally {
      setLoading(false);
    }
  };

  /**
   * 获取资产评价
   */
  const fetchReviews = async () => {
    if (!assetId) return;
    try {
      const response = await apiService.get<any>(`/marketplace/assets/${assetId}/reviews`);
      const data = response.data;
      setReviews(data?.items || []);
      setReviewTotal(data?.total || 0);
    } catch (error) {
      console.error('Failed to fetch reviews:', error);
    }
  };

  useEffect(() => {
    fetchAssetDetail();
    fetchReviews();
  }, [assetId]);

  /**
   * 获取状态标签颜色
   */
  const getStatusColor = (status?: string) => {
    const colorMap: Record<string, string> = {
      online: 'success',
      offline: 'default',
      maintenance: 'warning',
      pending: 'processing',
    };
    return colorMap[status || ''] || 'default';
  };

  /**
   * 获取能源来源中文
   */
  const getPowerSourceLabel = (source?: string) => {
    const map: Record<string, string> = {
      solar: '光伏', wind: '风电', grid: '电网', storage: '储能',
    };
    return map[source || ''] || source || '-';
  };

  const handleBuy = () => {
    navigate('/scheduling');
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', marginTop: 100 }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!asset) {
    return (
      <div style={{ textAlign: 'center', marginTop: 100 }}>
        <Empty description="资产不存在或已被下架" />
        <Button style={{ marginTop: 24 }} icon={<ArrowLeftOutlined />} onClick={() => navigate('/marketplace')}>
          返回市场
        </Button>
      </div>
    );
  }

  return (
    <div>
      {/* 顶部导航 */}
      <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/marketplace')} style={{ marginBottom: 16 }}>
        返回市场
      </Button>

      <Title level={2}>{asset.spec?.gpu || 'Unknown GPU'}</Title>
      <Paragraph type="secondary">
        {asset.type === 'compute' ? '算力资源' : asset.type === 'solar' ? '光伏资源' : asset.type}
      </Paragraph>

      {/* 基本信息卡片 */}
      <Card style={{ marginBottom: 24 }}>
        <Descriptions column={{ xs: 1, sm: 2, md: 4 }}>
          <Descriptions.Item label="资源ID">{asset.id}</Descriptions.Item>
          <Descriptions.Item label="状态">
            <Tag color={getStatusColor(asset.status)}>
              {asset.status === 'online' ? '在线' : asset.status === 'offline' ? '离线' : asset.status}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="类型">
            {asset.type === 'compute' ? '算力' : asset.type === 'storage' ? '存储' : asset.type}
          </Descriptions.Item>
          <Descriptions.Item label="可用区">{asset.location?.region || '-'}</Descriptions.Item>
        </Descriptions>
      </Card>

      <Row gutter={[16, 16]}>
        {/* 规格信息 */}
        <Col xs={24} md={12}>
          <Card title="规格信息" style={{ marginBottom: 16 }}>
            <Descriptions column={1} bordered>
              <Descriptions.Item label="GPU型号">{asset.spec?.gpu || '-'}</Descriptions.Item>
              <Descriptions.Item label="显存">{asset.spec?.vram || '-'}</Descriptions.Item>
              <Descriptions.Item label="CPU核心数">{asset.spec?.cpu_cores || '-'}</Descriptions.Item>
              <Descriptions.Item label="内存">{asset.spec?.memory_gb ? `${asset.spec.memory_gb} GB` : asset.spec?.ram || '-'}</Descriptions.Item>
              <Descriptions.Item label="存储容量">{asset.spec?.capacity_tb ? `${asset.spec.capacity_tb} TB` : '-'}</Descriptions.Item>
              <Descriptions.Item label="存储类型">{asset.spec?.storage_type || '-'}</Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>

        {/* 能源信息 */}
        <Col xs={24} md={12}>
          <Card title="能源信息" style={{ marginBottom: 16 }}>
            <Descriptions column={1} bordered>
              <Descriptions.Item label="能源来源">
                <Tag color="green"><FireOutlined /> {getPowerSourceLabel(asset.energy_profile?.power_source)}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="PUE">{asset.energy_profile?.PUE || '-'}</Descriptions.Item>
              <Descriptions.Item label="碳强度">{asset.energy_profile?.carbon_intensity ? `${asset.energy_profile.carbon_intensity} kg/kWh` : '-'}</Descriptions.Item>
              <Descriptions.Item label="电价">{asset.energy_profile?.price_per_kwh ? `¥${asset.energy_profile.price_per_kwh.toFixed(2)}/kWh` : '-'}</Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>
      </Row>

      {/* 定价信息 */}
      <Card title="定价信息" style={{ marginBottom: 24 }}>
        <Descriptions column={{ xs: 1, sm: 2, md: 4 }}>
          <Descriptions.Item label="计算价格">
            <Text strong style={{ fontSize: 20, color: '#f5222d' }}>
              ¥{asset.pricing?.compute_price_per_hour?.toFixed(2) || '0.00'}
            </Text>
            <Text type="secondary"> /小时</Text>
          </Descriptions.Item>
          <Descriptions.Item label="定价类型">
            {asset.pricing?.is_spot ? <Tag color="red">竞价实例</Tag> : <Tag color="blue">标准实例</Tag>}
          </Descriptions.Item>
          {asset.pricing?.is_spot && (
            <Descriptions.Item label="竞价折扣">
              {(asset.pricing.spot_discount || 0) * 100}%OFF
            </Descriptions.Item>
          )}
        </Descriptions>
        <div style={{ marginTop: 16 }}>
          <Button type="primary" size="large" icon={<ShoppingCartOutlined />} onClick={handleBuy}>
            立即购买
          </Button>
        </div>
      </Card>

      {/* 评价列表 */}
      <Card title="用户评价" extra={<span>共 {reviewTotal} 条评价</span>}>
        {reviews.length === 0 ? (
          <Empty description="暂无评价" />
        ) : (
          <Table
            dataSource={reviews}
            rowKey="id"
            pagination={false}
            columns={[
              { title: '评分', dataIndex: 'score', key: 'score', render: (v: number) => <Rate disabled defaultValue={v} /> },
              { title: '评价内容', dataIndex: 'text', key: 'text', ellipsis: true },
              { title: '用户', dataIndex: 'user_id', key: 'user_id', ellipsis: true },
              { title: '时间', dataIndex: 'created_at', key: 'created_at', width: 180 },
            ]}
          />
        )}
      </Card>
    </div>
  );
};

export default AssetDetailPage;
