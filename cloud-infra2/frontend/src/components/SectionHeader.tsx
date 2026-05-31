import React from 'react';

interface SectionHeaderProps {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
  className?: string;
}

const SectionHeader: React.FC<SectionHeaderProps> = ({ title, subtitle, action, className = '' }) => {
  return (
    <header className={`flex flex-col gap-4 md:flex-row md:items-end md:justify-between ${className}`}>
      <div>
        <h1 className="text-4xl font-bold tracking-tight text-slate-100">{title}</h1>
        {subtitle && <p className="mt-2 text-base text-slate-400">{subtitle}</p>}
      </div>
      {action && <div className="shrink-0">{action}</div>}
    </header>
  );
};

export default SectionHeader;
