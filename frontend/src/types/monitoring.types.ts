/**
 * 监控相关类型定义（与后端 monitoring.py Schema 对齐）
 */

export interface DataPoint {
  timestamp: string;
  value: number;
}

export interface MetricResponse {
  resource_id: string;
  metric: string;
  data_points: DataPoint[];
  aggregates: Record<string, number>;
}

export interface AlertRule {
  id: string;
  name: string;
  resource_id?: string;
  metric: string;
  condition: string; // gt / lt / eq / gte / lte
  threshold: number;
  duration_seconds: number;
  notify_channels: string;
  cooldown_seconds: number;
  is_active: number;
  last_triggered_at?: string;
  created_at?: string;
}

export interface AlertRuleCreateRequest {
  name: string;
  resource_id?: string;
  metric: string;
  condition: string;
  threshold: number;
  duration_seconds?: number;
  notify_channels?: string;
  cooldown_seconds?: number;
}

export interface AlertRuleUpdateRequest {
  name?: string;
  metric?: string;
  condition?: string;
  threshold?: number;
  duration_seconds?: number;
  notify_channels?: string;
  is_active?: number;
}

export interface Alert {
  id: string;
  rule_id?: string;
  resource_id: string;
  metric: string;
  value: number;
  threshold: number;
  condition: string;
  status: string;
  resolved_at?: string;
  message: string;
  created_at?: string;
}
