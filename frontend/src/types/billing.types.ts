/**
 * 账单相关类型定义（与后端 billing.py Schema 对齐）
 */

export interface MonthlyBill {
  id: string;
  user_id: string;
  year: number;
  month: number;
  total_amount: number;
  compute_fee: number;
  energy_fee: number;
  network_fee: number;
  storage_fee: number;
  green_cert_discount: number;
  actual_pay: number;
  order_count: number;
  status: string;
  created_at?: string;
}

export interface InvoiceCreateRequest {
  type: string; // normal / special
  title: string;
  tax_no: string;
  address?: string;
  phone?: string;
  bank_name?: string;
  bank_account?: string;
}

export interface Invoice {
  id: string;
  bill_id: string;
  type: string;
  title: string;
  amount: number;
  status: string;
  issued_at?: string;
}

export interface Reconciliation {
  total_orders: number;
  total_amount: number;
  total_payments: number;
  total_refunds: number;
  discrepancy: number;
  details: any[];
}
