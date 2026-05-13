/**
 * 支付服务 API
 * 与后端 /api/v1/payments/* 对齐
 */
import { apiService } from './api';
import type { PaymentCreateRequest, PaymentInfo } from '@/types/payment.types';

/**
 * 创建支付请求
 */
export const createPayment = (data: PaymentCreateRequest) =>
  apiService.post<{
    success: boolean;
    payment_id: string;
    payment_url?: string;
    qr_code?: string;
    message?: string;
  }>('/payments/create', data);

/**
 * 查询支付记录
 */
export const getPayment = (paymentId: string) =>
  apiService.get<PaymentInfo>(`/payments/${paymentId}`);

/**
 * 根据订单ID查询支付记录
 */
export const getPaymentByOrder = (orderId: string) =>
  apiService.get<PaymentInfo>(`/payments/order/${orderId}`);

/**
 * 开发用：模拟支付成功
 */
export const mockPay = (paymentId: string) =>
  apiService.get<{ success: boolean; message: string }>(
    `/payments/mock/pay/${paymentId}`
  );
