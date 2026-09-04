import { useState, useEffect } from 'react';
import { electronBridge } from '../services/electronBridge';

export function useElectron() {
  const [isElectron, setIsElectron] = useState(false);
  const [platform, setPlatform] = useState('browser');
  const [version, setVersion] = useState('1.0.0');

  useEffect(() => {
    const check = async () => {
      setIsElectron(electronBridge.isElectron());
      const p = await electronBridge.getPlatform();
      const v = await electronBridge.getVersion();
      setPlatform(p);
      setVersion(v);
    };
    check();
  }, []);

  return { isElectron, platform, version };
}
