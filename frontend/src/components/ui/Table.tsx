import { ReactNode } from 'react'
import { cn } from '../../utils/cn'

export function Table({
  children,
  className,
}: {
  children: ReactNode
  className?: string
}) {
  return (
    <div className={cn('overflow-x-auto', className)}>
      <table className="w-full border-collapse text-sm">{children}</table>
    </div>
  )
}

export function THead({ children }: { children: ReactNode }) {
  return <thead className="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-slate-600">{children}</thead>
}

export function TH({ children, className }: { children: ReactNode; className?: string }) {
  return <th className={cn('whitespace-nowrap border-b border-slate-200 px-4 py-3', className)}>{children}</th>
}

export function TBody({ children }: { children: ReactNode }) {
  return <tbody className="divide-y divide-slate-100">{children}</tbody>
}

export function TR({ children, className }: { children: ReactNode; className?: string }) {
  return <tr className={cn('hover:bg-slate-50/70', className)}>{children}</tr>
}

export function TD({ children, className }: { children: ReactNode; className?: string }) {
  return <td className={cn('px-4 py-3 align-top text-slate-700', className)}>{children}</td>
}

