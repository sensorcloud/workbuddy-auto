/**
 * 钱包服务 API
 * 与后端 /api/v1/wallet/* 对齐
 */
import { apiService } from './api';
import type { WalletBalance, WalletRechargeRequest, WalletWithdrawRequest, TransactionRecord } from '@/types/wallet.types';

/**
 * 获取钱包余额
 */
export const getBalance = () =>
  apiService.get<WalletBalance>('/wallet/balance');

/**
 * 充值
 */
export const recharge = (data: WalletRechargeRequest) =>
  apiService.post<{ payment_id: string; transaction_id: string; amount: number; payment_url?: string; status: string; message: string }>(
    '/wallet/recharge',
    data
  );

/**
 * 提现
 */
export const withdraw = (data: WalletWithdrawRequest) =>
  apiService.post<{ withdraw_id: string; amount: number; status: string; message: string }>(
    '/wallet/withdraw',
    data
  );

/**
 * 设置低余额告警阈值
 */
export const setLowBalanceAlert = (threshold: number) =>
  apiService.put<{ success: boolean; message: string }>(
    '/wallet/low-balance-alert',
    { threshold }
  );

/**
 * 获取交易流水
 */
export const getTransactions = (params?: {
  type?: string;
  page?: number;
  page_size?: number;
  start_date?: string;
  end_date?: string;
}) =>
  apiService.get<{
    items: TransactionRecord[];
    total: number;
    page: number;
    page_size: number;
  }>('/wallet/transactions', params);
