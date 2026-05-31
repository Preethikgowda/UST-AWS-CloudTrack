import React from 'react';

interface ContentGridProps {
  children: React.ReactNode;
  className?: string;
}

const ContentGrid: React.FC<ContentGridProps> = ({ children, className = '' }) => {
  return <div className={`grid gap-6 ${className}`}>{children}</div>;
};

export default ContentGrid;
