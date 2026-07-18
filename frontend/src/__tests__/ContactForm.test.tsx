import { act, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import ContactForm from '../components/ContactForm';
import { strings } from '../locales/ru';
import { submitContact } from '../services/api';

vi.mock('../services/api', () => ({
  submitContact: vi.fn(),
}));

const mockedSubmit = vi.mocked(submitContact);

beforeEach(() => {
  vi.useFakeTimers({ shouldAdvanceTime: true });
  mockedSubmit.mockReset();
});

afterEach(() => {
  vi.useRealTimers();
});

function renderForm() {
  return render(<ContactForm />);
}

describe('ContactForm', () => {
  it('renders all fields and submit button', () => {
    renderForm();

    expect(screen.getByPlaceholderText('Ваше имя')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Телефон')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Email')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Ваше сообщение...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: strings.contact.submit.idle })).toBeInTheDocument();
  });

  it('shows all validation errors on empty submit', async () => {
    renderForm();
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });

    await user.click(screen.getByRole('button', { name: strings.contact.submit.idle }));

    expect(screen.getByText(strings.contact.validation.name)).toBeInTheDocument();
    expect(screen.getByText(strings.contact.validation.phone)).toBeInTheDocument();
    expect(screen.getByText(strings.contact.validation.email)).toBeInTheDocument();
    expect(screen.getByText(strings.contact.validation.comment)).toBeInTheDocument();
  });

  it('shows name error for short name', async () => {
    renderForm();
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });

    await user.type(screen.getByPlaceholderText('Ваше имя'), 'A');
    await user.click(screen.getByRole('button', { name: strings.contact.submit.idle }));

    expect(screen.getByText(strings.contact.validation.name)).toBeInTheDocument();
  });

  it('shows email error for invalid email', async () => {
    renderForm();
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });

    await user.type(screen.getByPlaceholderText('Ваше имя'), 'Иван');
    await user.type(screen.getByPlaceholderText('Телефон'), '+79001234567');
    await user.type(screen.getByPlaceholderText('Email'), 'not-email');
    await user.type(screen.getByPlaceholderText('Ваше сообщение...'), 'Тестовое сообщение');
    await user.click(screen.getByRole('button', { name: strings.contact.submit.idle }));

    expect(screen.getByText(strings.contact.validation.email)).toBeInTheDocument();
  });

  it('shows comment error for short comment', async () => {
    renderForm();
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });

    await user.type(screen.getByPlaceholderText('Ваше имя'), 'Иван');
    await user.type(screen.getByPlaceholderText('Телефон'), '+79001234567');
    await user.type(screen.getByPlaceholderText('Email'), 'ivan@example.com');
    await user.type(screen.getByPlaceholderText('Ваше сообщение...'), 'Hi');
    await user.click(screen.getByRole('button', { name: strings.contact.submit.idle }));

    expect(screen.getByText(strings.contact.validation.comment)).toBeInTheDocument();
  });

  it('submits and shows success on valid data', async () => {
    mockedSubmit.mockResolvedValue({
      success: true,
      message: 'OK',
      id: '1',
      ai_analysis: null,
    });
    renderForm();
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });

    await user.type(screen.getByPlaceholderText('Ваше имя'), 'Иван');
    await user.type(screen.getByPlaceholderText('Телефон'), '+79001234567');
    await user.type(screen.getByPlaceholderText('Email'), 'ivan@example.com');
    await user.type(screen.getByPlaceholderText('Ваше сообщение...'), 'Тестовое сообщение');
    await user.click(screen.getByRole('button', { name: strings.contact.submit.idle }));

    expect(mockedSubmit).toHaveBeenCalledTimes(1);
    expect(screen.getByRole('status')).toHaveTextContent(strings.contact.success);
  });

  it('shows error when API fails', async () => {
    mockedSubmit.mockRejectedValue({
      success: false,
      message: 'Rate limit exceeded',
      status: 429,
    });
    renderForm();
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });

    await user.type(screen.getByPlaceholderText('Ваше имя'), 'Иван');
    await user.type(screen.getByPlaceholderText('Телефон'), '+79001234567');
    await user.type(screen.getByPlaceholderText('Email'), 'ivan@example.com');
    await user.type(screen.getByPlaceholderText('Ваше сообщение...'), 'Тестовое сообщение');
    await user.click(screen.getByRole('button', { name: strings.contact.submit.idle }));

    expect(screen.getByRole('alert')).toHaveTextContent('Rate limit exceeded');
  });

  it('auto-dismisses success after 5 seconds', async () => {
    mockedSubmit.mockResolvedValue({
      success: true,
      message: 'OK',
      id: '1',
      ai_analysis: null,
    });
    renderForm();
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });

    await user.type(screen.getByPlaceholderText('Ваше имя'), 'Иван');
    await user.type(screen.getByPlaceholderText('Телефон'), '+79001234567');
    await user.type(screen.getByPlaceholderText('Email'), 'ivan@example.com');
    await user.type(screen.getByPlaceholderText('Ваше сообщение...'), 'Тестовое сообщение');
    await user.click(screen.getByRole('button', { name: strings.contact.submit.idle }));

    expect(screen.getByRole('status')).toBeInTheDocument();

    await act(async () => {
      vi.advanceTimersByTime(5000);
    });

    expect(screen.queryByRole('status')).not.toBeInTheDocument();
  });

  it('clears field error on input', async () => {
    renderForm();
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });

    await user.click(screen.getByRole('button', { name: strings.contact.submit.idle }));
    expect(screen.getByText(strings.contact.validation.name)).toBeInTheDocument();

    await user.type(screen.getByPlaceholderText('Ваше имя'), 'Иван');
    expect(screen.queryByText(strings.contact.validation.name)).not.toBeInTheDocument();
  });

  it('disables button during loading', async () => {
    let resolveSubmit!: (value: {
      success: boolean;
      message: string;
      id: string;
      ai_analysis: null;
    }) => void;
    mockedSubmit.mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveSubmit = resolve;
        }),
    );
    renderForm();
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });

    await user.type(screen.getByPlaceholderText('Ваше имя'), 'Иван');
    await user.type(screen.getByPlaceholderText('Телефон'), '+79001234567');
    await user.type(screen.getByPlaceholderText('Email'), 'ivan@example.com');
    await user.type(screen.getByPlaceholderText('Ваше сообщение...'), 'Тестовое сообщение');
    await user.click(screen.getByRole('button', { name: strings.contact.submit.idle }));

    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
    expect(button).toHaveTextContent(strings.contact.submit.loading);

    resolveSubmit({ success: true, message: 'OK', id: '1', ai_analysis: null });
  });
});
