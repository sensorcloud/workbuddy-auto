/**
 * 监控服务 API
 * 与后端 /api/v1/monitoring/* 对齐
 */
import { apiService } from './api';
import type {
  MetricResponse,
  AlertRule,
  AlertRuleCreateRequest,
  AlertRuleUpdateRequest,
  Alert,
} from '@/types/monitoring.types';

/**
 * 查询历史指标数据
 */
export const queryMetrics = (
  resourceId: string,
  params: {
    metric: string;
    from_time: string;
    to_time: string;
    interval?: string;
  }
) =>
  apiService.get<MetricResponse>(
    `/monitoring/resources/${resourceId}/metrics`,
    params
  );

/**
 * 获取资源最新指标快照
 */
export const getLatestMetrics = (resourceId: string) =>
  apiService.get<{ resource_id: string; metrics: Record<string, number> }>(
    `/monitoring/resources/${resourceId}/latest`
  );

/**
 * 创建告警规则
 */
export const createAlertRule = (data: AlertRuleCreateRequest) =>
  apiService.post<AlertRule>('/monitoring/alert-rules', data);

/**
 * 获取告警规则列表
 */
export const listAlertRules = () =>
  apiService.get<AlertRule[]>('/monitoring/alert-rules');

/**
 * 更新告警规则
 */
export const updateAlertRule = (ruleId: string, data: AlertRuleUpdateRequest) =>
  apiService.put<AlertRule>(`/monitoring/alert-rules/${ruleId}`, data);

/**
 * 删除告警规则
 */
export const deleteAlertRule = (ruleId: string) =>
  apiService.delete<{ success: boolean }>(`/monitoring/alert-rules/${ruleId}`);

/**
 * 获取告警列表
 */
export const listAlerts = (params?: {
  status?: string;
  resource_id?: string;
  page?: number;
  page_size?: number;
}) =>
  apiService.get<{
    items: Alert[];
    total: number;
    page: number;
    page_size: number;
  }>('/monitoring/alerts', params);

/**
 * 手动解除告警
 */
export const resolveAlert = (alertId: string) =>
  apiService.put<Alert>(`/monitoring/alerts/${alertId}/resolve`);
