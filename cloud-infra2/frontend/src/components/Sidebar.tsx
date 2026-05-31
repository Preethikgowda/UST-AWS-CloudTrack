import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

type IconProps = {
  className?: string;
};

type NavItem = {
  label: string;
  path: string;
  icon: React.FC<IconProps>;
};

const iconClass = 'h-[21px] w-[21px] shrink-0';

const DashboardIcon: React.FC<IconProps> = ({ className }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <rect x="3.5" y="3.5" width="7" height="7" rx="1.8" />
    <rect x="13.5" y="3.5" width="7" height="7" rx="1.8" />
    <rect x="3.5" y="13.5" width="7" height="7" rx="1.8" />
    <rect x="13.5" y="13.5" width="7" height="7" rx="1.8" />
  </svg>
);

const PortfolioIcon: React.FC<IconProps> = ({ className }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M9 7V5.8A2.3 2.3 0 0 1 11.3 3.5h1.4A2.3 2.3 0 0 1 15 5.8V7" />
    <rect x="3.5" y="7" width="17" height="13.5" rx="2.5" />
    <path d="M3.5 12.2h17" />
    <path d="M10 12.2v1.5h4v-1.5" />
  </svg>
);

const AllocationIcon: React.FC<IconProps> = ({ className }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M12 3.5v17" />
    <path d="M3.5 12h17" />
    <path d="M6.5 6.5h3" />
    <path d="M14.5 6.5h3" />
    <path d="M6.5 17.5h3" />
    <path d="M14.5 17.5h3" />
  </svg>
);

const HistoryIcon: React.FC<IconProps> = ({ className }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M4 6.5v5h5" />
    <path d="M4.8 11.5a7.5 7.5 0 1 0 2.3-5.4L4 9.2" />
    <path d="M12 8v4.4l3 1.8" />
  </svg>
);

const ProfileIcon: React.FC<IconProps> = ({ className }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <circle cx="12" cy="8" r="3.8" />
    <path d="M4.8 20.5a7.2 7.2 0 0 1 14.4 0" />
  </svg>
);

const AdminIcon: React.FC<IconProps> = ({ className }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M12 3.5 19 7v5.3c0 4.1-2.8 7.1-7 8.2-4.2-1.1-7-4.1-7-8.2V7l7-3.5Z" />
    <path d="m9.5 12 1.7 1.7 3.5-3.7" />
  </svg>
);

const LogoutIcon: React.FC<IconProps> = ({ className }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M10 5H6.8A2.3 2.3 0 0 0 4.5 7.3v9.4A2.3 2.3 0 0 0 6.8 19H10" />
    <path d="M14.5 8.5 18 12l-3.5 3.5" />
    <path d="M18 12H9" />
  </svg>
);

const CollapseIcon: React.FC<IconProps & { collapsed: boolean }> = ({ className, collapsed }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d={collapsed ? 'm10 7 5 5-5 5' : 'm14 7-5 5 5 5'} />
    <path d="M19 4v16" />
  </svg>
);

const navItems: NavItem[] = [
  { label: 'Dashboard', path: '/dashboard', icon: DashboardIcon },
  { label: 'Portfolio', path: '/portfolio', icon: PortfolioIcon },
  { label: 'Allocation', path: '/allocation', icon: AllocationIcon },
  { label: 'History', path: '/history', icon: HistoryIcon },
  { label: 'Profile', path: '/profile', icon: ProfileIcon },
];

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  collapsed: boolean;
  onCollapseToggle: () => void;
  width: number;
  isMobile: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onToggle, collapsed, onCollapseToggle, width, isMobile }) => {
  const { user, logout } = useAuth();
  const isCollapsed = collapsed && !isMobile;
  const items = user?.role === 'admin' ? [...navItems, { label: 'Admin', path: '/admin', icon: AdminIcon }] : navItems;

  return (
    <>
      {isOpen && <button className="fixed inset-0 z-40 bg-black/60 md:hidden" onClick={onToggle} aria-label="Close menu" />}

      <aside
        className={`fixed left-0 top-0 z-50 flex h-screen flex-col overflow-hidden border-r border-slate-800 bg-[#0b1222] transition-[width,transform] duration-300 ease-in-out md:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
        style={{ width }}
      >
        <div className={`flex h-20 shrink-0 items-center border-b border-slate-800 ${isCollapsed ? 'justify-center px-0' : 'px-6'}`}>
          <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-violet-500">
            <span className="text-sm font-bold text-white">IW</span>
          </div>
          {!isCollapsed && (
            <div className="ml-3 min-w-0">
              <p className="truncate text-sm font-semibold text-slate-100">IntelliWealth</p>
              <p className="truncate text-xs text-slate-400">Enterprise Suite</p>
            </div>
          )}
        </div>

        <nav className={`flex min-h-0 flex-1 flex-col gap-2 overflow-y-auto py-6 ${isCollapsed ? 'px-[18px]' : 'px-4'}`}>
          {items.map((item) => {
            const Icon = item.icon;

            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={() => isMobile && onToggle()}
                title={isCollapsed ? item.label : undefined}
                className={({ isActive }) =>
                  `group relative flex h-[52px] items-center rounded-xl text-sm font-medium transition-all duration-200 ease-in-out ${
                    isCollapsed ? 'justify-center px-0' : 'gap-3 pl-5 pr-4'
                  } ${
                    isActive
                      ? 'bg-[rgba(99,102,241,.18)] text-indigo-100'
                      : 'text-slate-300 hover:bg-slate-800/70 hover:text-slate-100'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    {isActive && <span className="absolute left-0 top-1/2 h-7 w-1 -translate-y-1/2 rounded-r-full bg-indigo-400" />}
                    <span className="flex h-6 w-6 shrink-0 items-center justify-center">
                      <Icon className={iconClass} />
                    </span>
                    {!isCollapsed && <span className="truncate leading-none">{item.label}</span>}
                  </>
                )}
              </NavLink>
            );
          })}
        </nav>

        <footer className={`shrink-0 border-t border-slate-800 ${isCollapsed ? 'px-[18px] py-4' : 'p-4'}`}>
          <div className={`mb-3 flex items-center ${isCollapsed ? 'justify-center' : 'gap-3'}`}>
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-violet-500 text-sm font-semibold text-white">
              {user?.name?.charAt(0).toUpperCase() || 'U'}
            </div>
            {!isCollapsed && (
              <div className="min-w-0">
                <p className="truncate text-sm font-medium text-slate-200">{user?.name || 'User'}</p>
                <p className="truncate text-xs capitalize text-slate-400">{user?.role || 'member'}</p>
              </div>
            )}
          </div>

          <div className="flex flex-col gap-2">
            {!isMobile && (
              <button
                onClick={onCollapseToggle}
                className={`flex h-11 items-center rounded-xl border border-slate-700 text-xs font-medium text-slate-300 transition hover:bg-slate-800 ${
                  isCollapsed ? 'justify-center px-0' : 'justify-center gap-2 px-3'
                }`}
                title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
              >
                <CollapseIcon collapsed={isCollapsed} className="h-5 w-5 shrink-0" />
                {!isCollapsed && <span>{isCollapsed ? 'Expand' : 'Collapse'}</span>}
              </button>
            )}
            <button
              onClick={logout}
              className={`flex h-11 items-center rounded-xl border border-slate-700 text-xs font-medium text-slate-300 transition hover:bg-slate-800 ${
                isCollapsed ? 'justify-center px-0' : 'justify-center gap-2 px-3'
              }`}
              title={isCollapsed ? 'Logout' : undefined}
            >
              <LogoutIcon className="h-5 w-5 shrink-0" />
              {!isCollapsed && <span>Logout</span>}
            </button>
          </div>
        </footer>
      </aside>
    </>
  );
};

export default Sidebar;
