import { ReactNode } from 'react'
import { cn } from '../../utils/cn'

export function Card({
  className,
  children,
}: {
  className?: string
  children: ReactNode
}) {
  return (
    <div
      className={cn(
        'rounded-xl border border-slate-200 bg-white shadow-sm',
        className,
      )}
    >
      {children}
    </div>
  )
}

export function CardHeader({
  className,
  title,
  description,
  actions,
}: {
  className?: string
  title: ReactNode
  description?: ReactNode
  actions?: ReactNode
}) {
  return (
    <div className={cn('flex items-start justify-between gap-4 border-b border-slate-200 p-4', className)}>
      <div className="min-w-0">
        <div className="text-sm font-semibold text-slate-900">{title}</div>
        {description ? <div className="mt-1 text-sm text-slate-600">{description}</div> : null}
      </div>
      {actions ? <div className="shrink-0">{actions}</div> : null}
    </div>
  )
}

export function CardContent({ className, children }: { className?: string; children: ReactNode }) {
  return <div className={cn('p-4', className)}>{children}</div>
}

export function CardFooter({ className, children }: { className?: string; children: ReactNode }) {
  return <div className={cn('border-t border-slate-200 p-4', className)}>{children}</div>
}

