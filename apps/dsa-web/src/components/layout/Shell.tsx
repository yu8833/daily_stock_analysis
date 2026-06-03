import type React from 'react';
import { useEffect, useState } from 'react';
import { Menu, ChevronLeft, ChevronRight } from 'lucide-react';
import { Outlet } from 'react-router-dom';
import { Drawer } from '../common/Drawer';
import { SidebarNav } from './SidebarNav';
import { cn } from '../../utils/cn';
import { ThemeToggle } from '../theme/ThemeToggle';

type ShellProps = {
  children?: React.ReactNode;
};

export const Shell: React.FC<ShellProps> = ({ children }) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    if (!mobileOpen) {
      return undefined;
    }

    const handleResize = () => {
      if (window.innerWidth >= 1024) {
        setMobileOpen(false);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [mobileOpen]);

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="pointer-events-none fixed inset-x-0 top-3 z-40 flex items-start justify-between px-3 lg:hidden">
        <button
          type="button"
          onClick={() => setMobileOpen(true)}
          className="pointer-events-auto inline-flex h-10 w-10 items-center justify-center rounded-xl border border-border/70 bg-card/85 text-secondary-text shadow-soft-card backdrop-blur-md transition-colors hover:bg-hover hover:text-foreground"
          aria-label="打开导航菜单"
        >
          <Menu className="h-5 w-5" />
        </button>
        <div className="pointer-events-auto">
          <ThemeToggle />
        </div>
      </div>

      <div className="mx-auto flex min-h-screen w-full max-w-[1680px] p-1 sm:p-1.5 lg:p-2">
        <aside
          className={cn(
            'sticky top-1.5 z-40 hidden shrink-0 overflow-visible rounded-2xl border border-[var(--shell-sidebar-border)] bg-card/72 shadow-soft-card backdrop-blur-sm transition-[width,margin] duration-200 lg:flex',
            'max-h-[calc(100vh-1rem)] self-start sm:top-2 sm:max-h-[calc(100vh-1rem)]',
            collapsed ? 'w-[64px]' : 'w-[140px]'
          )}
          aria-label="桌面侧边导航"
        >
          <div className="flex flex-col h-full w-full">
            <SidebarNav collapsed={collapsed} onNavigate={() => setMobileOpen(false)} />
            <button
              type="button"
              onClick={() => setCollapsed(!collapsed)}
              className="mt-auto flex items-center justify-center p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
              aria-label={collapsed ? '展开菜单' : '收起菜单'}
            >
              {collapsed ? <ChevronRight className="h-5 w-5" /> : <ChevronLeft className="h-5 w-5" />}
            </button>
          </div>
        </aside>

        <main className="min-h-0 min-w-0 flex-1 pt-12 lg:pl-2 lg:pt-0 touch-pan-y">
          {children ?? <Outlet />}
        </main>
      </div>

      <Drawer
        isOpen={mobileOpen}
        onClose={() => setMobileOpen(false)}
        title="导航菜单"
        width="max-w-xs"
        zIndex={90}
        side="left"
      >
        <SidebarNav onNavigate={() => setMobileOpen(false)} />
      </Drawer>
    </div>
  );
};
