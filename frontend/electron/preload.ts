/**
 * Electron Preload Script with Context Isolation.
 * Exposes a secure, typed bridge between the web frontend and Electron main process.
 */
import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electronAPI', {
  getPlatform: () => ipcRenderer.invoke('get-platform'),
  getVersion: () => ipcRenderer.invoke('get-version'),
  sendIpcMessage: (channel: string, data: unknown) => {
    const validChannels = ['system:ping', 'window:minimize', 'window:maximize', 'window:close'];
    if (validChannels.includes(channel)) {
      ipcRenderer.send(channel, data);
    }
  },
  onIpcMessage: (channel: string, callback: (data: unknown) => void) => {
    const validChannels = ['backend:status', 'system:alert'];
    if (validChannels.includes(channel)) {
      const subscription = (_event: Electron.IpcRendererEvent, data: unknown) => callback(data);
      ipcRenderer.on(channel, subscription);
      return () => ipcRenderer.removeListener(channel, subscription);
    }
    return () => {};
  },
});
