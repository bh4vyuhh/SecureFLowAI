import React, { useState, useCallback } from 'react';
import Sidebar from './Sidebar';
import Topbar from './Topbar';
import ToastContainer from '../ui/Toast';

export const AppLayout = ({ children }) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const toggleSidebar = useCallback(() => setSidebarCollapsed(v => !v), []);

  return (
    <div className="app-shell">
      <div className="app-sidebar" style={{
        width: sidebarCollapsed ? 0 : undefined,
        overflow: sidebarCollapsed ? 'hidden' : undefined,
        opacity: sidebarCollapsed ? 0 : 1,
        transition: 'width 0.25s ease, opacity 0.25s ease',
      }}>
        <Sidebar />
      </div>

      <div className="app-main" style={{
        marginLeft: sidebarCollapsed ? 0 : undefined,
        transition: 'margin-left 0.25s ease',
      }}>
        <div className="app-topbar-wrapper" style={{
          left: sidebarCollapsed ? 0 : undefined,
          transition: 'left 0.25s ease',
        }}>
          <Topbar onToggleMenu={toggleSidebar} />
        </div>

        <main className="app-content">
          {children}
        </main>
      </div>

      <ToastContainer />
    </div>
  );
};

export default AppLayout;
