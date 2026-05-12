import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { apiService } from '@/services/api';

/**
 * 用户类型定义
 */
interface User {
  id: string;
  username: string;
  email: string;
  role: 'consumer' | 'provider' | 'admin';
}

/**
 * 认证状态类型定义
 */
interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  accessToken: string | null; // alias for token, used by api.ts interceptor

  // 操作方法
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string, email: string, role: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => void;
  refreshToken: () => Promise<boolean>;
}

/**
 * 认证Store
 * 管理用户认证状态，连接真实后端API
 */
export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      isAuthenticated: false,
      user: null,
      token: null,
      accessToken: null,

      /**
       * 登录 - 调用后端 /api/v1/auth/login
       */
      login: async (username: string, password: string) => {
        const response = await apiService.post<{
          access_token: string;
          token_type: string;
          user: User;
        }>('/auth/login', { username, password });

        const { access_token, user } = response.data || response as any;

        set({
          isAuthenticated: true,
          user: user || {
            id: 'unknown',
            username,
            email: '',
            role: 'consumer',
          },
          token: access_token,
          accessToken: access_token,
        });
      },

      /**
       * 注册 - 调用后端 /api/v1/auth/register
       */
      register: async (username: string, password: string, email: string, role: string) => {
        const response = await apiService.post<{
          access_token: string;
          token_type: string;
          user: User;
        }>('/auth/register', { username, email, password, role });

        const { access_token, user } = response.data || response as any;

        // 注册成功后自动登录
        set({
          isAuthenticated: true,
          user: user || {
            id: 'unknown',
            username,
            email,
            role: role as 'consumer' | 'provider',
          },
          token: access_token,
          accessToken: access_token,
        });
      },

      /**
       * 退出登录
       */
      logout: () => {
        set({
          isAuthenticated: false,
          user: null,
          token: null,
          accessToken: null,
        });
      },

      /**
       * 检查认证状态
       */
      checkAuth: () => {
        const state = get();
        if (!state.token && !state.accessToken) {
          set({ isAuthenticated: false, user: null });
        }
      },

      /**
       * 刷新Token（占位实现）
       */
      refreshToken: async () => {
        // 当前版本不支持 refresh token，直接返回 false
        return false;
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        isAuthenticated: state.isAuthenticated,
        user: state.user,
        token: state.token,
        accessToken: state.accessToken,
      }),
    }
  )
);
