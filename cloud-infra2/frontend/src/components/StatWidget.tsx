import React from 'react';

interface StatWidgetProps {
  label: string;
  value: string;
  detail?: string;
}

const StatWidget: React.FC<StatWidgetProps> = ({ label, value, detail }) => {
  return (
    <article className="app-card p-7">
      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">{label}</p>
      <p className="mt-3 text-3xl font-semibold text-slate-100">{value}</p>
      {detail && <p className="mt-2 text-sm text-slate-400">{detail}</p>}
    </article>
  );
};

export default StatWidget;
