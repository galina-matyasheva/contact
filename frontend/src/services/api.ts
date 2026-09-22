import { strings } from '../locales/ru';
import type { ApiError, ContactFormData, ContactResponse } from '../types';

const API_BASE = 'https://galina-contact-api.onrender.com/api';

export async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  });

  const data = await response.json();

  if (!response.ok) {
    const error: ApiError = {
      success: false,
      message: data.message || strings.api.fallbackError,
      errors: data.errors || [],
      status: response.status,
    };
    throw error;
  }

  return data as T;
}

export async function submitContact(
  formData: ContactFormData,
  signal?: AbortSignal,
): Promise<ContactResponse> {
  return request<ContactResponse>('/contact', {
    method: 'POST',
    body: JSON.stringify(formData),
    signal,
  });
}
