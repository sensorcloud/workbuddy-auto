import React, { ErrorInfo, ReactNode, Error } from 'react';
import { Result, Button, Typography } from 'antd';

const { Text } = Typography;

/**
 * 错误边界组件Props
 */
interface ErrorBoundaryProps {
  children: ReactNode;
}

/**
 * 错误边界组件State
 */
interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

/**
 * 全局错误边界组件
 * 捕获子组件树中的JavaScript错误，记录错误并显示降级UI
 */
class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({
      error,
      errorInfo,
    });
  }

  handleReload = (): void => {
    this.setState({ hasError: false, error: null, errorInfo: null });
    window.location.reload();
  };

  handleGoHome = (): void => {
    this.setState({ hasError: false, error: null, errorInfo: null });
    window.location.href = '/';
  };

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        <Result
          status="error"
          title="页面出现错误"
          subTitle={this.state.error?.message || '未知错误'}
          extra={[
            <Button type="primary" key="reload" onClick={this.handleReload}>
              重新加载
            </Button>,
            <Button key="home" onClick={this.handleGoHome}>
              返回首页
            </Button>,
          ]}
        >
          {process.env.NODE_ENV === 'development' && this.state.errorInfo && (
            <details style={{ marginTop: '16px', textAlign: 'left' }}>
              <Text type="danger">错误堆栈：</Text>
              <pre style={{ background: '#f5f5f5', padding: '12px', borderRadius: '4px' }}>
                {this.state.error?.stack}
                {this.state.errorInfo.componentStack}
              </pre>
            </details>
          )}
        </Result>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
