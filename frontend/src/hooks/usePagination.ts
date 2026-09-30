import { useState, useCallback } from 'react';

interface UsePaginationOptions {
  initialPage?: number;
  initialPageSize?: number;
}

interface UsePaginationReturn {
  page: number;
  pageSize: number;
  goToPage: (page: number) => void;
  nextPage: () => void;
  prevPage: () => void;
  setPageSize: (size: number) => void;
  reset: () => void;
}

export function usePagination(options: UsePaginationOptions = {}): UsePaginationReturn {
  const [page, setPage] = useState(options.initialPage || 1);
  const [pageSize, setPageSizeState] = useState(options.initialPageSize || 10);

  const goToPage = useCallback((newPage: number) => {
    if (newPage >= 1) {
      setPage(newPage);
    }
  }, []);

  const nextPage = useCallback(() => {
    setPage((prev) => prev + 1);
  }, []);

  const prevPage = useCallback(() => {
    setPage((prev) => (prev > 1 ? prev - 1 : 1));
  }, []);

  const setPageSize = useCallback((size: number) => {
    setPageSizeState(size);
    setPage(1); // Reset to first page when changing page size
  }, []);

  const reset = useCallback(() => {
    setPage(options.initialPage || 1);
    setPageSizeState(options.initialPageSize || 10);
  }, [options.initialPage, options.initialPageSize]);

  return {
    page,
    pageSize,
    goToPage,
    nextPage,
    prevPage,
    setPageSize,
    reset,
  };
}
