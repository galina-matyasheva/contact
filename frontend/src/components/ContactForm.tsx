import { useEffect, useRef, useState } from 'react';

import { strings } from '../locales/ru';
import { submitContact } from '../services/api';
import type { ApiError, ContactFormData } from '../types';

const initialForm: ContactFormData = {
  name: '',
  phone: '',
  email: '',
  comment: '',
};

type FieldErrors = Partial<Record<keyof ContactFormData, string>>;

export default function ContactForm() {
  const [form, setForm] = useState<ContactFormData>(initialForm);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    return () => abortRef.current?.abort();
  }, []);

  useEffect(() => {
    if (!success) return;
    const timer = setTimeout(() => setSuccess(false), 5000);
    return () => clearTimeout(timer);
  }, [success]);

  const validate = (): boolean => {
    const errors: FieldErrors = {};

    if (form.name.trim().length < 2) {
      errors.name = strings.contact.validation.name;
    }
    if (form.phone.trim().length < 6) {
      errors.phone = strings.contact.validation.phone;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
      errors.email = strings.contact.validation.email;
    }
    if (form.comment.trim().length < 5) {
      errors.comment = strings.contact.validation.comment;
    }

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    const field = name as keyof ContactFormData;
    setForm((prev) => ({ ...prev, [field]: value }));
    if (fieldErrors[field]) {
      setFieldErrors((prev) => {
        const next = { ...prev };
        delete next[field];
        return next;
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);

    if (!validate()) return;

    abortRef.current?.abort();
    abortRef.current = new AbortController();

    setLoading(true);
    try {
      await submitContact(form, abortRef.current.signal);
      setSuccess(true);
      setForm(initialForm);
    } catch (err: unknown) {
      if (err instanceof DOMException && err.name === 'AbortError') return;
      const message =
        err && typeof err === 'object' && 'message' in err
          ? (err as ApiError).message
          : strings.contact.submit.error;
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const inputClass = (field: keyof ContactFormData) =>
    `w-full px-4 py-3 rounded-lg border bg-white/5 backdrop-blur-sm text-white placeholder-gray-400 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-cyan-400/50 focus:border-cyan-400 ${
      fieldErrors[field] ? 'border-red-400' : 'border-white/10'
    }`;

  const { fields } = strings.contact;

  return (
    <section id="contact" className="px-6 py-20">
      <div className="mx-auto max-w-2xl">
        <h2 className="mb-4 text-center text-3xl font-bold text-white md:text-4xl">
          {strings.contact.heading}
        </h2>
        <p className="mb-10 text-center text-gray-400">{strings.contact.subtitle}</p>

        {success && (
          <div
            className="mb-6 rounded-lg border border-green-500/30 bg-green-500/10 p-4 text-center text-green-300"
            role="status"
          >
            {strings.contact.success}
          </div>
        )}

        {error && (
          <div
            className="mb-6 rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-center text-red-300"
            role="alert"
          >
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5" noValidate>
          <div>
            <label htmlFor="name" className="sr-only">
              {fields.name.label}
            </label>
            <input
              type="text"
              id="name"
              name="name"
              placeholder={fields.name.placeholder}
              autoComplete="name"
              required
              aria-invalid={!!fieldErrors.name}
              aria-describedby={fieldErrors.name ? 'name-error' : undefined}
              value={form.name}
              onChange={handleChange}
              className={inputClass('name')}
            />
            {fieldErrors.name && (
              <p id="name-error" className="mt-1 text-sm text-red-400" role="alert">
                {fieldErrors.name}
              </p>
            )}
          </div>

          <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
            <div>
              <label htmlFor="phone" className="sr-only">
                {fields.phone.label}
              </label>
              <input
                type="tel"
                id="phone"
                name="phone"
                placeholder={fields.phone.placeholder}
                autoComplete="tel"
                required
                aria-invalid={!!fieldErrors.phone}
                aria-describedby={fieldErrors.phone ? 'phone-error' : undefined}
                value={form.phone}
                onChange={handleChange}
                className={inputClass('phone')}
              />
              {fieldErrors.phone && (
                <p id="phone-error" className="mt-1 text-sm text-red-400" role="alert">
                  {fieldErrors.phone}
                </p>
              )}
            </div>
            <div>
              <label htmlFor="email" className="sr-only">
                {fields.email.label}
              </label>
              <input
                type="email"
                id="email"
                name="email"
                placeholder={fields.email.placeholder}
                autoComplete="email"
                required
                aria-invalid={!!fieldErrors.email}
                aria-describedby={fieldErrors.email ? 'email-error' : undefined}
                value={form.email}
                onChange={handleChange}
                className={inputClass('email')}
              />
              {fieldErrors.email && (
                <p id="email-error" className="mt-1 text-sm text-red-400" role="alert">
                  {fieldErrors.email}
                </p>
              )}
            </div>
          </div>

          <div>
            <label htmlFor="comment" className="sr-only">
              {fields.comment.label}
            </label>
            <textarea
              id="comment"
              name="comment"
              placeholder={fields.comment.placeholder}
              rows={5}
              required
              aria-invalid={!!fieldErrors.comment}
              aria-describedby={fieldErrors.comment ? 'comment-error' : undefined}
              value={form.comment}
              onChange={handleChange}
              className={inputClass('comment')}
            />
            {fieldErrors.comment && (
              <p id="comment-error" className="mt-1 text-sm text-red-400" role="alert">
                {fieldErrors.comment}
              </p>
            )}
          </div>

          <button
            type="submit"
            disabled={loading}
            aria-busy={loading}
            className="w-full cursor-pointer rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 px-6 py-3 font-semibold text-white transition-all duration-200 hover:from-cyan-400 hover:to-blue-500 hover:shadow-lg hover:shadow-cyan-500/25 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="h-5 w-5 animate-spin" viewBox="0 0 24 24">
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                    fill="none"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                  />
                </svg>
                {strings.contact.submit.loading}
              </span>
            ) : (
              strings.contact.submit.idle
            )}
          </button>
        </form>
      </div>
    </section>
  );
}
