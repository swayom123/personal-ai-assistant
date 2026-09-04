import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from '../components/Sidebar';
import { TopBar } from '../components/TopBar';
import { useAppStore } from '../stores/appStore';
import { cn } from '../utils/cn';

export const AppLayout: React.FC = () => {
  const { sidebarOpen } = useAppStore();

  return (
    <div className="min-h-screen bg-background text-text-primary flex">
      <Sidebar />
      <div
        className={cn(
          'flex-1 flex flex-col min-w-0 transition-all duration-300',
          sidebarOpen ? 'ml-64' : 'ml-20'
        )}
      >
        <TopBar />
        <main className="mt-16 flex-1 p-6 md:p-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
