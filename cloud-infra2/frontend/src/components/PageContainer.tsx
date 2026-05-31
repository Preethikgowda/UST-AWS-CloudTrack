import React from 'react';

interface PageContainerProps {
  children: React.ReactNode;
  className?: string;
}

const PageContainer: React.FC<PageContainerProps> = ({ children, className = '' }) => {
  return (
    <main className={`w-full ${className}`}>
      <div className="mx-auto w-full max-w-[1600px] px-4 py-4 md:px-6 md:py-6 xl:px-10 xl:py-8">
        {children}
      </div>
    </main>
  );
};

export default PageContainer;
