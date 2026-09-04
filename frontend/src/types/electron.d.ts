export interface IElectronAPI {
  getPlatform: () => Promise<string>;
  getVersion: () => Promise<string>;
  sendIpcMessage: (channel: string, data: unknown) => void;
  onIpcMessage: (channel: string, callback: (data: unknown) => void) => () => void;
}

declare global {
  interface Window {
    electronAPI?: IElectronAPI;
  }
}
