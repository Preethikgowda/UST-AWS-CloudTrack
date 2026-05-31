import React from 'react';

interface MetricCardProps {
  label: string;
  value: string;
  change?: string;
  positive?: boolean;
}

const MetricCard: React.FC<MetricCardProps> = ({ label, value, change, positive = true }) => {
  return (
    <article className="app-card flex min-h-[140px] flex-col justify-between p-7">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">{label}</p>
      <div className="flex items-end justify-between gap-4">
        <p className="text-3xl font-semibold text-slate-100">{value}</p>
        {change && (
          <span className={`text-sm font-semibold ${positive ? 'text-emerald-400' : 'text-rose-400'}`}>
            {change}
          </span>
        )}
      </div>
    </article>
  );
};

export default MetricCard;
