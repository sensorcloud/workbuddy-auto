/**
 * 钱包相关类型定义（与后端 WalletBalanceResponse 对齐）
 */

export interface WalletBalance {
  balance: number;
  frozen: number;
  available: number;
  total_recharge: number;
  total_withdraw: number;
  total_consume: number;
  credit_limit: number;
  low_balance_alert: number;
}

export interface WalletRechargeRequest {
  amount: number;
  channel: string; // alipay / wechat / bankcard
}

export interface WalletWithdrawRequest {
  amount: number;
  bank_card: string;
  bank_name: string;
  account_name: string;
}

export interface TransactionRecord {
  id: string;
  type: string; // recharge / freeze / unfreeze / consume / refund / withdraw
  amount: number;
  balance_after: number;
  order_id?: string;
  remark?: string;
  created_at?: string;
}

export interface RechargeResult {
  payment_id: string;
  transaction_id: string;
  amount: number;
  payment_url?: string;
  status: string;
  message: string;
}

export interface WithdrawResult {
  withdraw_id: string;
  amount: number;
  status: string;
  message: string;
}

export interface TransactionListResponse {
  items: TransactionRecord[];
  total: number;
  page: number;
  page_size: number;
}
