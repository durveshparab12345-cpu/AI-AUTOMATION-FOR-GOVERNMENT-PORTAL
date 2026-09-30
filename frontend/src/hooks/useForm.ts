import { useState, useCallback, ChangeEvent, FormEvent } from 'react';
import type { FormError } from '../types';

interface UseFormOptions<T> {
  initialValues: T;
  onSubmit: (values: T) => Promise<void> | void;
  validate?: (values: T) => FormError[];
}

interface UseFormReturn<T> {
  values: T;
  errors: Record<string, string>;
  touched: Record<string, boolean>;
  loading: boolean;
  success: boolean;
  handleChange: (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => void;
  handleBlur: (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => void;
  handleSubmit: (e: FormEvent<HTMLFormElement>) => Promise<void>;
  setFieldValue: (field: string, value: unknown) => void;
  reset: () => void;
}

export function useForm<T>(options: UseFormOptions<T>): UseFormReturn<T> {
  const [values, setValues] = useState<T>(options.initialValues);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleChange = useCallback((
    e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target;
    const fieldValue = type === 'checkbox' ? (e.target as HTMLInputElement).checked : value;

    setValues((prev) => ({
      ...prev,
      [name]: fieldValue,
    }));
  }, []);

  const handleBlur = useCallback((
    e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name } = e.target;
    setTouched((prev) => ({
      ...prev,
      [name]: true,
    }));
  }, []);

  const handleSubmit = useCallback(
    async (e: FormEvent<HTMLFormElement>) => {
      e.preventDefault();

      // Validate if validator provided
      if (options.validate) {
        const validationErrors = options.validate(values);
        const errorMap = validationErrors.reduce((acc, err) => {
          acc[err.field] = err.message;
          return acc;
        }, {} as Record<string, string>);

        if (Object.keys(errorMap).length > 0) {
          setErrors(errorMap);
          return;
        }
      }

      setLoading(true);
      setSuccess(false);
      setErrors({});

      try {
        await options.onSubmit(values);
        setSuccess(true);
      } catch (err: unknown) {
        const errorMessage = err instanceof Error ? err.message : 'Submission failed';
        setErrors({ _general: errorMessage });
      } finally {
        setLoading(false);
      }
    },
    [values, options]
  );

  const setFieldValue = useCallback((field: string, value: unknown) => {
    setValues((prev) => ({
      ...prev,
      [field]: value,
    }));
  }, []);

  const reset = useCallback(() => {
    setValues(options.initialValues);
    setErrors({});
    setTouched({});
    setSuccess(false);
  }, [options.initialValues]);

  return {
    values,
    errors,
    touched,
    loading,
    success,
    handleChange,
    handleBlur,
    handleSubmit,
    setFieldValue,
    reset,
  };
}
