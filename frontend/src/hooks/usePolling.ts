import { useEffect, useRef } from 'react';

/**
 * Hook for polling an async function at regular intervals
 */
export function usePolling(
  callback: () => Promise<void>,
  interval: number,
  enabled: boolean = true
): void {
  const intervalIdRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (!enabled) {
      if (intervalIdRef.current) {
        clearInterval(intervalIdRef.current);
        intervalIdRef.current = null;
      }
      return;
    }

    // Call immediately on enable
    callback();

    // Then set up recurring interval
    intervalIdRef.current = setInterval(() => {
      callback();
    }, interval);

    return () => {
      if (intervalIdRef.current) {
        clearInterval(intervalIdRef.current);
        intervalIdRef.current = null;
      }
    };
  }, [callback, interval, enabled]);
}
