/**
 * 资产相关类型定义
 */

/**
 * 资产状态枚举
 */
export enum AssetStatus {
  PENDING = 'pending',
  ONLINE = 'online',
  OFFLINE = 'offline',
  MAINTENANCE = 'maintenance',
}

/**
 * 资产审核状态枚举
 */
export enum AuditStatus {
  PENDING = 'pending',
  APPROVED = 'approved',
  REJECTED = 'rejected',
}

/**
 * 资产类型枚举
 */
export enum AssetType {
  COMPUTE = 'compute',
  STORAGE = 'storage',
  SOLAR = 'solar',
  GRID = 'grid',
}

/**
 * 能源来源枚举
 */
export enum PowerSource {
  GRID = 'grid',
  SOLAR = 'solar',
  WIND = 'wind',
  STORAGE = 'storage',
}

/**
 * 资产规格（与后端 spec JSON 字段对齐）
 */
export interface AssetSpec {
  gpu?: string;
  vram?: string;
  cpu_cores?: number;
  memory_gb?: number;
  /** 兼容旧数据 */
  cpu?: string;
  ram?: string;
  /** 存储类资产 */
  capacity_tb?: number;
  storage_type?: string;
}

/**
 * 能源配置（与后端 energy_profile JSON 字段对齐）
 */
export interface EnergyProfile {
  power_source: string;
  PUE?: number;
  carbon_intensity?: number;
  price_per_kwh?: number;
  carbon_factor?: number;
}

/**
 * 定价信息（与后端 pricing JSON 字段对齐）
 */
export interface PricingInfo {
  compute_price_per_hour: number;
  is_spot?: boolean;
  spot_discount?: number;
  storage_price_per_day?: number;
  /** 兼容旧字段 */
  storage_price_per_gb_month?: number;
}

/**
 * 位置信息（与后端 location JSON 字段对齐）
 */
export interface LocationInfo {
  region?: string;
  zone?: string;
  datacenter_id?: string;
  /** 兼容旧字段 */
  datacenter?: string;
}

/**
 * 资产数据接口（与后端 AssetResponse 对齐）
 */
export interface Asset {
  id: string;
  owner_id?: string;
  type: string;
  spec?: AssetSpec;
  energy_profile?: EnergyProfile;
  pricing?: PricingInfo;
  status: string;
  location?: LocationInfo;
  audit_status?: string;
  audit_comment?: string;
  created_at?: string;
  updated_at?: string;
}

/**
 * 资产注册请求
 */
export interface AssetRegisterRequest {
  owner_id: string;
  type: string;
  spec: AssetSpec;
  energy_profile: EnergyProfile;
  pricing: PricingInfo;
  location?: LocationInfo;
}
