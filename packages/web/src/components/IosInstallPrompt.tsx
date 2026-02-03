/**
 * IosInstallPrompt - Minimal add-to-home-screen hint for iOS Safari.
 */
import { useEffect, useState } from 'react';
import './IosInstallPrompt.css';

const DISMISS_KEY = 'ios_install_prompt_dismissed';

function isIosSafari(): boolean {
  const ua = navigator.userAgent || navigator.vendor || '';
  const isIOS = /iPad|iPhone|iPod/.test(ua);
  const isSafari = /Safari/.test(ua) && !/CriOS|FxiOS|OPiOS|EdgiOS/.test(ua);
  return isIOS && isSafari;
}

function isStandalone(): boolean {
  return window.matchMedia('(display-mode: standalone)').matches || (navigator as any).standalone === true;
}

export default function IosInstallPrompt() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (!isIosSafari()) return;
    if (isStandalone()) return;
    if (localStorage.getItem(DISMISS_KEY) === '1') return;
    setVisible(true);
  }, []);

  if (!visible) return null;

  return (
    <div className="ios-install-prompt" role="region" aria-label="Install Kapp">
      <div className="ios-install-content">
        <strong>Install Kapp</strong>
        <span>Tap Share and then “Add to Home Screen”.</span>
      </div>
      <button
        className="ios-install-dismiss"
        type="button"
        onClick={() => {
          localStorage.setItem(DISMISS_KEY, '1');
          setVisible(false);
        }}
        aria-label="Dismiss install prompt"
      >
        ×
      </button>
    </div>
  );
}
