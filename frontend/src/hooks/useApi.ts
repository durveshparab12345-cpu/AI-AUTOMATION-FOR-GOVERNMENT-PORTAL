import { useState, useCallback } from 'react';
import { getToken } from '../services/api';
import { useApi } from '../types';

const BASE_URL = '/api/v1';

interface UseApiOptions {
  baseUrl?: string;
  headers?: Record<string, string>;
}

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export function useApi<T>(options: UseApiOptions = {}) {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const baseUrl = options.baseUrl || BASE_URL;
  const defaultHeaders = options.headers || {};

  const request = useCallback(
    async (endpoint: string, fetchOptions: RequestInit = {}): Promise<T | null> => {
      setState({ data: null, loading: true, error: null });

      try {
        const headers: Record<string, string> = {
          'Content-Type': 'application/json',
          ...defaultHeaders,
          ...(fetchOptions.headers as Record<string, string> || {}),
        };

        const token = getToken();
        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
        }

        const url = endpoint.startsWith('http') ? endpoint : `${baseUrl}${endpoint}`;
        const response = await fetch(url, {
          ...fetchOptions,
          headers,
        });

        if (!response.ok) {
          const errorBody = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }));
          throw new Error(errorBody.detail || `HTTP ${response.status}`);
        }

        const data = await response.json() as T;
        setState({ data, loading: false, error: null });
        return data;
      } catch (err: unknown) {
        const errorMessage = err instanceof Error ? err.message : 'An error occurred';
        setState({ data: null, loading: false, error: errorMessage });
        return null;
      }
    },
    [baseUrl, defaultHeaders]
  );

  return {
    ...state,
    request,
  };
}
