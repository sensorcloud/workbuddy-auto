import axios, { AxiosInstance, AxiosError, AxiosRequestConfig } from 'axios';
import { message } from 'antd';
import { useAuthStore } from '@/store/authStore';

/**
 * 统一API响应格式（后端可能返回的格式）
 */
export interface ApiResponse<T = any> {
  code?: number;
  message?: string;
  data?: T;
  [key: string]: any; // 允许直接返回的字段
}

/**
 * 创建Axios实例
 */
const createApiInstance = (): AxiosInstance => {
  const instance = axios.create({
    baseURL: '/api/v1',
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  /**
   * 请求拦截器
   * - 自动附加JWT Token
   * - 添加时间戳防止缓存
   */
  instance.interceptors.request.use(
    (config: AxiosRequestConfig) => {
      const token = useAuthStore.getState().accessToken || useAuthStore.getState().token;
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }

      // 添加时间戳防止缓存
      if (config.method === 'get') {
        config.params = {
          ...config.params,
          _t: Date.now(),
        };
      }

      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  /**
   * 响应拦截器
   * - 统一错误处理
   * - 兼容两种返回格式：{code, message, data} 和 直接返回数据
   */
  instance.interceptors.response.use(
    (response) => {
      // 直接返回响应，让调用方处理数据格式
      return response;
    },
    async (error: AxiosError<ApiResponse>) => {
      const { response, config } = error;

      // 401错误 - Token过期
      if (response?.status === 401) {
        const authStore = useAuthStore.getState();

        try {
          // 尝试刷新Token
          const refreshed = await authStore.refreshToken();

          if (refreshed && config) {
            // 重试原请求
            const newToken = authStore.accessToken || authStore.token;
            (config as any).headers.Authorization = `Bearer ${newToken}`;
            return instance(config);
          }
        } catch (refreshError) {
          // 刷新失败，跳转到登录页
          authStore.logout();
          message.error('会话已过期，请重新登录');
          window.location.href = '/login';
        }
      }

      // 其他错误
      const errorMessage =
        (response?.data as any)?.detail ||
        (response?.data as any)?.message ||
        error.message ||
        '网络错误';
      message.error(errorMessage);

      return Promise.reject(error);
    }
  );

  return instance;
};

/**
 * API实例（单例）
 */
export const api = createApiInstance();

/**
 * 通用请求方法
 * 自动提取响应数据：优先取 data 字段，否则直接返回
 */
export const apiService = {
  get: <T = any>(url: string, params?: any) =>
    api.get<ApiResponse<T> | T>(url, { params }).then((res) => {
      const d = res.data;
      // 如果是 {code, message, data} 格式
      if (d && typeof d === 'object' && 'code' in d && 'data' in d) {
        return { data: d.data as T, code: d.code, message: d.message };
      }
      // 直接返回数据
      return { data: d as T };
    }),

  post: <T = any>(url: string, data?: any) =>
    api.post<ApiResponse<T> | T>(url, data).then((res) => {
      const d = res.data;
      if (d && typeof d === 'object' && 'code' in d && 'data' in d) {
        return { data: d.data as T, code: d.code, message: d.message };
      }
      return { data: d as T };
    }),

  put: <T = any>(url: string, data?: any) =>
    api.put<ApiResponse<T> | T>(url, data).then((res) => {
      const d = res.data;
      if (d && typeof d === 'object' && 'code' in d && 'data' in d) {
        return { data: d.data as T, code: d.code, message: d.message };
      }
      return { data: d as T };
    }),

  delete: <T = any>(url: string, params?: any) =>
    api.delete<ApiResponse<T> | T>(url, { params }).then((res) => {
      const d = res.data;
      if (d && typeof d === 'object' && 'code' in d && 'data' in d) {
        return { data: d.data as T, code: d.code, message: d.message };
      }
      return { data: d as T };
    }),
};

export default api;
