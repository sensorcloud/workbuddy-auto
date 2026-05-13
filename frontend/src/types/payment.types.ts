/**
 * 支付相关类型定义（与后端 payment.py Schema 对齐）
 */

export interface PaymentCreateRequest {
  order_id: string;
  channel: string; // balance / alipay / wechat / bankcard
}

export interface PaymentInfo {
  id: string;
  order_id: string;
  user_id: string;
  channel: string;
  amount: number;
  status: string;
  trade_no?: string;
  paid_at?: string;
  payment_url?: string;
  qr_code?: string;
  created_at?: string;
}
