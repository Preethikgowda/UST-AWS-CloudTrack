import React from 'react';

interface TableCardProps {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}

const TableCard: React.FC<TableCardProps> = ({ title, subtitle, action, children, className = '' }) => {
  return (
    <section className={`app-card p-7 ${className}`}>
      <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-100">{title}</h2>
          {subtitle && <p className="mt-1 text-sm text-slate-400">{subtitle}</p>}
        </div>
        {action && <div>{action}</div>}
      </div>
      {children}
    </section>
  );
};

export default TableCard;
