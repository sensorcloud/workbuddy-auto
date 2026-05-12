/**
 * 订单相关类型定义（与后端 OrderResponse / Quote 对齐）
 */

/**
 * 任务类型枚举
 */
export enum TaskType {
  INFERENCE = 'inference',
  TRAINING = 'training',
  RENDER = 'render',
}

/**
 * 调度策略枚举
 */
export enum StrategyType {
  CHEAPEST = 'cheapest',
  FASTEST = 'fastest',
  GREENEST = 'greenest',
  CUSTOM = 'custom',
}

/**
 * 订单状态枚举
 */
export enum OrderStatus {
  PENDING = 'pending',
  PAID = 'paid',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
}

/**
 * 支付方式枚举
 */
export enum PaymentMethod {
  BALANCE = 'balance',
  ALIPAY = 'alipay',
  WECHAT = 'wechat',
  BANK_TRANSFER = 'bank_transfer',
}

/**
 * 报价信息（与后端 scheduling_service quote 对齐）
 */
export interface Quote {
  asset_id: string;
  provider_id?: string;
  compute_cost: number;
  energy_cost: number;
  total_cost: number;
  estimated_carbon_kg?: number;
  carbon_saved_kg?: number;
  match_reason?: string;
}

/**
 * 任务状态（与后端 monitoring /tasks/{task_id} 对齐）
 */
export interface TaskStatus {
  task_id?: string;
  id?: string;
  order_id?: string;
  asset_id?: string;
  status: string;
  progress?: number;
  start_time?: string;
  started_at?: string;
  estimated_end_time?: string;
  finished_at?: string;
  running_hours?: number;
  total_cost?: number;
  estimated_remaining?: string;
  current_power_kw?: number;
  total_compute_cost?: number;
  total_energy_cost?: number;
  total_carbon_kg?: number;
  real_time_metrics?: {
    power_kw: number[];
    carbon_kg: number[];
  };
}

/**
 * 订单数据接口（与后端 OrderResponse 对齐）
 */
export interface Order {
  id: string;
  user_id: string;
  asset_id?: string;
  task_type?: string;
  strategy?: string;
  estimated_duration_hours?: number;
  selected_quote?: Quote;
  status: string;
  compute_cost?: number;
  energy_cost?: number;
  total_cost?: number;
  container_image?: string;
  dataset_location?: string;
  payment_id?: string;
  carbon_report_id?: string;
  created_at?: string;
  updated_at?: string;
  started_at?: string;
  completed_at?: string;
}

/**
 * 订单创建请求（与后端 OrderCreate 对齐）
 */
export interface OrderCreateRequest {
  user_id: string;
  asset_id: string;
  selected_quote?: Record<string, any>;
  container_image?: string;
  dataset_location?: string;
  task_type?: string;
  estimated_duration_hours?: number;
}

/**
 * 任务提交请求（与后端 TaskSubmitRequest 对齐）
 */
export interface TaskSubmitRequest {
  selected_quote: Record<string, any>;
  container_image?: string;
  dataset_location?: string;
  task_type?: string;
  estimated_duration_hours?: number;
}
