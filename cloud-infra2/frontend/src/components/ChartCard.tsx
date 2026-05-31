import React from 'react';

interface ChartCardProps {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  className?: string;
}

const ChartCard: React.FC<ChartCardProps> = ({ title, subtitle, children, className = '' }) => {
  return (
    <section className={`app-card p-7 ${className}`}>
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-slate-100">{title}</h2>
        {subtitle && <p className="mt-1 text-sm text-slate-400">{subtitle}</p>}
      </div>
      {children}
    </section>
  );
};

export default ChartCard;
