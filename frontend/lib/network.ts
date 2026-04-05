import { useState, useEffect } from "react";

/** Returns true when the browser has network connectivity. SSR-safe. */
export function useOnlineStatus(): boolean {
  const [online, setOnline] = useState(true);

  useEffect(() => {
    // Only runs on the client — safe to access navigator and window here
    setOnline(navigator.onLine);

    const up   = () => setOnline(true);
    const down = () => setOnline(false);
    window.addEventListener("online",  up);
    window.addEventListener("offline", down);
    return () => {
      window.removeEventListener("online",  up);
      window.removeEventListener("offline", down);
    };
  }, []);

  return online;
}
