import { InputHTMLAttributes, ReactNode, SelectHTMLAttributes, TextareaHTMLAttributes } from 'react'
import { cn } from '../../utils/cn'

export function Field({
  label,
  hint,
  error,
  required,
  children,
  className,
}: {
  label: string
  hint?: ReactNode
  error?: ReactNode
  required?: boolean
  children: ReactNode
  className?: string
}) {
  return (
    <div className={cn('space-y-1.5', className)}>
      <div className="flex items-center justify-between gap-3">
        <label className="text-sm font-medium text-slate-800">
          {label} {required ? <span className="text-rose-600">*</span> : null}
        </label>
        {hint ? <div className="text-xs text-slate-500">{hint}</div> : null}
      </div>
      {children}
      {error ? <div className="text-sm text-rose-700">{error}</div> : null}
    </div>
  )
}

export function TextInput({
  className,
  hasError,
  ...props
}: InputHTMLAttributes<HTMLInputElement> & { hasError?: boolean }) {
  return (
    <input
      className={cn(
        'h-10 w-full rounded-lg border bg-white px-3 text-sm text-slate-900 shadow-sm outline-none transition focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100',
        hasError ? 'border-rose-300 focus:border-rose-500 focus:ring-rose-100' : 'border-slate-300',
        className,
      )}
      {...props}
    />
  )
}

export function NumberInput({
  className,
  hasError,
  ...props
}: InputHTMLAttributes<HTMLInputElement> & { hasError?: boolean }) {
  return <TextInput className={className} hasError={hasError} type="number" {...props} />
}

export function Select({
  className,
  hasError,
  ...props
}: SelectHTMLAttributes<HTMLSelectElement> & { hasError?: boolean }) {
  return (
    <select
      className={cn(
        'h-10 w-full rounded-lg border bg-white px-3 text-sm text-slate-900 shadow-sm outline-none transition focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100',
        hasError ? 'border-rose-300 focus:border-rose-500 focus:ring-rose-100' : 'border-slate-300',
        className,
      )}
      {...props}
    />
  )
}

export function TextArea({
  className,
  hasError,
  ...props
}: TextareaHTMLAttributes<HTMLTextAreaElement> & { hasError?: boolean }) {
  return (
    <textarea
      className={cn(
        'w-full rounded-lg border bg-white px-3 py-2 text-sm text-slate-900 shadow-sm outline-none transition focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100',
        hasError ? 'border-rose-300 focus:border-rose-500 focus:ring-rose-100' : 'border-slate-300',
        className,
      )}
      {...props}
    />
  )
}

