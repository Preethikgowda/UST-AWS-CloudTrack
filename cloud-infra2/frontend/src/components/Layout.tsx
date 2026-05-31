import React, { useEffect, useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Navbar from './Navbar';
import PageContainer from './PageContainer';

const SIDEBAR_EXPANDED = 280;
const SIDEBAR_COLLAPSED = 88;

const Layout: React.FC = () => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(() => window.innerWidth >= 768 && window.innerWidth < 1024);
  const [viewportWidth, setViewportWidth] = useState(window.innerWidth);

  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      setViewportWidth(width);

      if (width < 768) {
        setCollapsed(false);
        setMobileOpen(false);
      } else if (width < 1024) {
        setCollapsed(true);
        setMobileOpen(false);
      } else {
        setCollapsed(false);
        setMobileOpen(false);
      }
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const isMobile = viewportWidth < 768;
  const sidebarWidth = isMobile ? SIDEBAR_EXPANDED : collapsed ? SIDEBAR_COLLAPSED : SIDEBAR_EXPANDED;
  const contentOffset = isMobile ? 0 : sidebarWidth;

  return (
    <div className="min-h-screen bg-[#020617] text-slate-100">
      <Sidebar
        isOpen={mobileOpen}
        collapsed={collapsed}
        width={sidebarWidth}
        isMobile={isMobile}
        onToggle={() => setMobileOpen((value) => !value)}
        onCollapseToggle={() => setCollapsed((value) => !value)}
      />

      <div className="min-h-screen flex-1 transition-[margin-left] duration-300 ease-in-out" style={{ marginLeft: contentOffset }}>
        <Navbar onMenuToggle={() => setMobileOpen((value) => !value)} />
        <PageContainer>
          <Outlet />
        </PageContainer>
      </div>
    </div>
  );
};

export default Layout;
