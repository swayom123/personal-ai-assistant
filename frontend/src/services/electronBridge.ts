/**
 * Desktop architecture bridge for Electron.
 * Provides safe fallback for web browsers while preparing IPC integration.
 */
export const electronBridge = {
  isElectron: (): boolean => {
    return typeof window !== 'undefined' && Boolean(window.electronAPI);
  },

  getPlatform: async (): Promise<string> => {
    if (window.electronAPI) {
      return window.electronAPI.getPlatform();
    }
    return navigator.platform || 'Web Browser';
  },

  getVersion: async (): Promise<string> => {
    if (window.electronAPI) {
      return window.electronAPI.getVersion();
    }
    return '1.0.0-web';
  },
};
