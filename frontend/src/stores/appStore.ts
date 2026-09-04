import { create } from 'zustand';
import { HealthResponse } from '../types/api';

interface AppState {
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  health: HealthResponse | null;
  healthLoading: boolean;
  healthError: string | null;
  setHealth: (health: HealthResponse | null) => void;
  setHealthLoading: (loading: boolean) => void;
  setHealthError: (error: string | null) => void;
}

export const useAppStore = create<AppState>((set) => ({
  sidebarOpen: true,
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setSidebarOpen: (open: boolean) => set({ sidebarOpen: open }),
  health: null,
  healthLoading: false,
  healthError: null,
  setHealth: (health) => set({ health, healthError: null }),
  setHealthLoading: (loading) => set({ healthLoading: loading }),
  setHealthError: (error) => set({ healthError: error, health: null }),
}));
