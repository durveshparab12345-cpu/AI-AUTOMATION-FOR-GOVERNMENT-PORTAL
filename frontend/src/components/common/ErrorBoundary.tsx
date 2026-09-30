import { Component, ReactNode, ErrorInfo } from 'react';

interface Props {
  children: ReactNode;
  fallback?: (error: Error, retry: () => void) => ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  reset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError && this.state.error) {
      return this.props.fallback ? (
        this.props.fallback(this.state.error, this.reset)
      ) : (
        <div
          style={{
            padding: '2rem',
            background: '#1e293b',
            border: '1px solid #7c2d12',
            borderRadius: '10px',
            color: '#fca5a5',
          }}
        >
          <h2 style={{ margin: '0 0 1rem', color: '#f87171' }}>Something went wrong</h2>
          <p style={{ margin: '0 0 1rem', fontSize: '0.9rem' }}>
            {this.state.error.message}
          </p>
          <button
            onClick={this.reset}
            style={{
              background: '#7c2d12',
              color: '#fff',
              border: 'none',
              padding: '0.6rem 1rem',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '0.9rem',
              fontWeight: 600,
            }}
          >
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
