/**
 * 账单服务 API
 * 与后端 /api/v1/billing/* 对齐
 */
import { apiService } from './api';
import type { MonthlyBill, InvoiceCreateRequest, Invoice, Reconciliation } from '@/types/billing.types';

/**
 * 获取月度账单
 */
export const getMonthlyBill = (year: number, month: number) =>
  apiService.get<MonthlyBill>('/billing/monthly', { year, month });

/**
 * 手动生成月度账单
 */
export const generateBill = (year: number, month: number) =>
  apiService.post<MonthlyBill>('/billing/generate', { year, month });

/**
 * 账单列表
 */
export const listBills = (params?: { page?: number; page_size?: number }) =>
  apiService.get<{
    items: MonthlyBill[];
    total: number;
    page: number;
    page_size: number;
  }>('/billing/list', params);

/**
 * 申请发票
 */
export const createInvoice = (billId: string, data: InvoiceCreateRequest) =>
  apiService.post<Invoice>(`/billing/${billId}/invoice`, data);

/**
 * 发票列表
 */
export const listInvoices = (params?: {
  bill_id?: string;
  status?: string;
  page?: number;
  page_size?: number;
}) =>
  apiService.get<{
    items: Invoice[];
    total: number;
    page: number;
    page_size: number;
  }>('/billing/invoices', params);

/**
 * 对账管理
 */
export const getReconciliation = (startDate: string, endDate: string) =>
  apiService.get<Reconciliation>('/billing/reconciliation', {
    start_date: startDate,
    end_date: endDate,
  });
