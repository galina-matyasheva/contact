import { beforeEach, describe, expect, it, vi } from 'vitest';

import { request, submitContact } from '../services/api';
import type { ContactFormData } from '../types';

const mockFetch = vi.fn();

beforeEach(() => {
  vi.stubGlobal('fetch', mockFetch);
  mockFetch.mockReset();
});

function jsonResponse(data: unknown, ok = true, status = 200) {
  return {
    ok,
    status,
    json: () => Promise.resolve(data),
  } as Response;
}

describe('request', () => {
  it('returns parsed JSON on success', async () => {
    const payload = { success: true, id: '123' };
    mockFetch.mockResolvedValue(jsonResponse(payload));

    const result = await request<typeof payload>('/contact');

    expect(result).toEqual(payload);
    expect(mockFetch).toHaveBeenCalledWith('/api/contact', {
      headers: { 'Content-Type': 'application/json' },
    });
  });

  it('throws ApiError on non-ok response', async () => {
    mockFetch.mockResolvedValue(
      jsonResponse({ message: 'Validation error', errors: [] }, false, 422),
    );

    await expect(request('/contact')).rejects.toMatchObject({
      success: false,
      message: 'Validation error',
      errors: [],
      status: 422,
    });
  });

  it('uses fallback message when response has no message', async () => {
    mockFetch.mockResolvedValue(jsonResponse({}, false, 500));

    await expect(request('/contact')).rejects.toMatchObject({
      success: false,
      message: 'Произошла ошибка',
      status: 500,
    });
  });

  it('includes errors array from response', async () => {
    const errors = [{ field: 'body → email', message: 'Invalid email' }];
    mockFetch.mockResolvedValue(jsonResponse({ message: 'Validation failed', errors }, false, 422));

    await expect(request('/contact')).rejects.toMatchObject({
      errors,
      status: 422,
    });
  });
});

describe('submitContact', () => {
  const formData: ContactFormData = {
    name: 'Иван',
    phone: '+79001234567',
    email: 'ivan@example.com',
    comment: 'Тестовое сообщение',
  };

  it('sends POST with correct body', async () => {
    const response = {
      success: true,
      message: 'OK',
      id: '1',
      ai_analysis: null,
    };
    mockFetch.mockResolvedValue(jsonResponse(response));

    await submitContact(formData);

    expect(mockFetch).toHaveBeenCalledWith('/api/contact', {
      method: 'POST',
      body: JSON.stringify(formData),
      headers: { 'Content-Type': 'application/json' },
      signal: undefined,
    });
  });

  it('passes AbortSignal to fetch', async () => {
    const controller = new AbortController();
    mockFetch.mockResolvedValue(
      jsonResponse({ success: true, message: 'OK', id: '1', ai_analysis: null }),
    );

    await submitContact(formData, controller.signal);

    expect(mockFetch).toHaveBeenCalledWith(
      '/api/contact',
      expect.objectContaining({ signal: controller.signal }),
    );
  });
});
