import { useState, useRef, useCallback } from "react";
import { HappyRobotVoiceClient } from "@happyrobot-ai/sdk/voice";
import type { VoiceConnection } from "@happyrobot-ai/sdk/voice";

/** Empty = use same origin + Vite proxy → works on localhost:5173, 5174, 5175, … */
const VOICE_SERVER = (import.meta.env.VITE_VOICE_SERVER_URL || "").replace(/\/$/, "");
const TOKEN_URL = VOICE_SERVER ? `${VOICE_SERVER}/api/voice/token` : "/api/voice/token";

const DASHBOARD_URL =
  import.meta.env.VITE_DASHBOARD_URL ||
  "https://happy-robot-fde-production-f148.up.railway.app/dashboard";

type LogEntry = {
  time: string;
  message: string;
  type: "info" | "success" | "error" | "event";
};

function timestamp() {
  return new Date().toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [elapsed, setElapsed] = useState(0);
  const connectionRef = useRef<VoiceConnection | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const addLog = useCallback(
    (message: string, type: LogEntry["type"] = "info") => {
      setLogs((prev) => [...prev, { time: timestamp(), message, type }]);
    },
    []
  );

  const startTimer = useCallback(() => {
    setElapsed(0);
    timerRef.current = setInterval(() => setElapsed((e) => e + 1), 1000);
  }, []);

  const stopTimer = useCallback(() => {
    if (timerRef.current) clearInterval(timerRef.current);
    timerRef.current = null;
  }, []);

  const startCall = useCallback(async () => {
    setIsConnecting(true);
    addLog("Requesting voice token from server...", "info");

    try {
      const res = await fetch(TOKEN_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });

      if (!res.ok) {
        const err = (await res.json().catch(() => ({}))) as {
          error?: string;
          detail?: string;
          hint?: string;
          status?: number;
        };
        const parts = [
          err.detail || err.error,
          err.hint,
          `HTTP ${err.status ?? res.status}`,
        ].filter(Boolean);
        throw new Error(parts.join(" — ") || `Server returned ${res.status}`);
      }

      const { url, token, room_name, run_id } = await res.json();
      addLog(`Token received. Room: ${room_name}`, "success");
      addLog(`Run ID: ${run_id}`, "info");

      const voiceClient = new HappyRobotVoiceClient({ url, token });

      const connection = await voiceClient.connect({
        onConnected: () => {
          setIsConnected(true);
          setIsConnecting(false);
          addLog("Connected to voice room", "success");
          startTimer();
        },
        onDisconnected: () => {
          setIsConnected(false);
          setIsMuted(false);
          setIsConnecting(false);
          connectionRef.current = null;
          stopTimer();
          addLog("Disconnected from voice room", "event");
        },
        onAgentConnected: (participant) => {
          addLog(`Agent joined: ${participant.identity}`, "success");
        },
        onReconnecting: () => {
          addLog("Connection lost, reconnecting...", "event");
        },
        onReconnected: () => {
          addLog("Reconnected successfully", "success");
        },
        onError: (err) => {
          addLog(`Error: ${err.message || err}`, "error");
          setIsConnecting(false);
        },
      });

      connectionRef.current = connection;
    } catch (err: unknown) {
      let msg = err instanceof Error ? err.message : String(err);
      if (msg === "Failed to fetch") {
        msg =
          "Failed to fetch — start token server (cd server && npm run dev, port 3001). Restart Vite after pull so the /api/voice proxy applies.";
      }
      addLog(`Failed to start call: ${msg}`, "error");
      setIsConnecting(false);
    }
  }, [addLog, startTimer, stopTimer]);

  const endCall = useCallback(async () => {
    addLog("Ending call...", "info");
    await connectionRef.current?.disconnect();
    connectionRef.current = null;
    setIsConnected(false);
    setIsMuted(false);
    stopTimer();
  }, [addLog, stopTimer]);

  const toggleMute = useCallback(async () => {
    if (!connectionRef.current) return;
    if (isMuted) {
      await connectionRef.current.unmute();
      setIsMuted(false);
      addLog("Microphone unmuted", "info");
    } else {
      await connectionRef.current.mute();
      setIsMuted(true);
      addLog("Microphone muted", "info");
    }
  }, [isMuted, addLog]);

  const formatTime = (s: number) => {
    const m = Math.floor(s / 60);
    const sec = s % 60;
    return `${m.toString().padStart(2, "0")}:${sec.toString().padStart(2, "0")}`;
  };

  return (
    <div style={styles.page}>
      {/* Sidebar accent */}
      <div style={styles.sidebar}>
        <div style={styles.sidebarLogo}>
          <img src="/logo.png" alt="" width={32} height={32} style={{ borderRadius: 6, objectFit: "contain" }} />
          <span style={styles.sidebarTitle}>Acme Logistics</span>
        </div>
        <div style={styles.sidebarSection}>Voice Test Client</div>
        <div style={{ ...styles.sidebarLink, ...styles.sidebarLinkActive }}>
          <PhoneIcon />
          Inbound Call Sim
        </div>
        <a href={DASHBOARD_URL} target="_blank" rel="noopener noreferrer" style={{ ...styles.sidebarLink, textDecoration: "none" }}>
          <DashIcon />
          Dashboard
        </a>
        <div style={styles.sidebarSpacer} />
        <div style={styles.sidebarFooter}>Powered by HappyRobot AI</div>
      </div>

      {/* Main area */}
      <div style={styles.main}>
        <div style={styles.topbar}>
          <img src="/logo.png" alt="Acme Logistics" width={32} height={32} style={{ borderRadius: 6, objectFit: "contain" }} />
          <span style={styles.topbarTitle}>Inbound Call Simulator</span>
          <div style={styles.topbarDivider} />
          <span style={styles.topbarSub}>Web SDK Test Client</span>
          <div style={{ flex: 1 }} />
          {isConnected && (
            <div style={styles.liveBadge}>
              <div style={styles.liveDot} />
              <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: "0.8rem" }}>
                {formatTime(elapsed)}
              </span>
            </div>
          )}
        </div>

        <div style={styles.content}>
          {/* Call control card */}
          <div style={styles.callCard}>
            <div style={styles.callVisual}>
              <div
                style={{
                  ...styles.callCircle,
                  ...(isConnected ? styles.callCircleActive : {}),
                  ...(isConnecting ? styles.callCirclePending : {}),
                }}
              >
                {isConnected ? (
                  <WaveIcon />
                ) : isConnecting ? (
                  <SpinnerIcon />
                ) : (
                  <PhoneIcon size={32} />
                )}
              </div>
              <div style={styles.callStatus}>
                {isConnected
                  ? "Call in progress"
                  : isConnecting
                  ? "Connecting..."
                  : "Ready to test"}
              </div>
              <div style={styles.callHint}>
                {isConnected
                  ? "Simulate a carrier: provide an MC number, request a load, negotiate pricing"
                  : isConnecting
                  ? "Establishing WebRTC connection..."
                  : "Click Start Call to connect to your HappyRobot voice agent"}
              </div>
            </div>

            <div style={styles.controls}>
              {!isConnected && !isConnecting && (
                <button style={styles.btnStart} onClick={startCall}>
                  <PhoneIcon size={18} /> Start Call
                </button>
              )}
              {isConnected && (
                <>
                  <button
                    style={isMuted ? styles.btnMuted : styles.btnMute}
                    onClick={toggleMute}
                  >
                    {isMuted ? <MicOffIcon /> : <MicIcon />}
                    {isMuted ? "Unmute" : "Mute"}
                  </button>
                  <button style={styles.btnEnd} onClick={endCall}>
                    <PhoneOffIcon /> End Call
                  </button>
                </>
              )}
              {isConnecting && (
                <button style={styles.btnDisabled} disabled>
                  Connecting...
                </button>
              )}
            </div>
          </div>

          {/* Event log */}
          <div style={styles.logCard}>
            <div style={styles.logHeader}>
              <span style={styles.logTitle}>Event Log</span>
              <span style={styles.logCount}>{logs.length} events</span>
            </div>
            <div style={styles.logBody}>
              {logs.length === 0 ? (
                <div style={styles.logEmpty}>Events will appear here when you start a call</div>
              ) : (
                logs.map((log, i) => (
                  <div key={i} style={styles.logRow}>
                    <span style={styles.logTime}>{log.time}</span>
                    <span
                      style={{
                        ...styles.logDot,
                        background:
                          log.type === "success"
                            ? "#22C55E"
                            : log.type === "error"
                            ? "#EF4444"
                            : log.type === "event"
                            ? "#F97316"
                            : "#3B82F6",
                      }}
                    />
                    <span style={styles.logMsg}>{log.message}</span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function PhoneIcon({ size = 18 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6A19.79 19.79 0 0 1 2.12 4.18 2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.362 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.338 1.85.573 2.81.7A2 2 0 0 1 22 16.92z" />
    </svg>
  );
}

function PhoneOffIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M10.68 13.31a16 16 0 0 0 3.41 2.6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.338 1.85.573 2.81.7A2 2 0 0 1 22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.42 19.42 0 0 1-3.33-2.67" />
      <path d="M14.91 7.09a16 16 0 0 0-2.6-3.41L8.09 9.91" />
      <line x1="1" y1="1" x2="23" y2="23" />
    </svg>
  );
}

function MicIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
      <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
      <line x1="12" y1="19" x2="12" y2="23" />
      <line x1="8" y1="23" x2="16" y2="23" />
    </svg>
  );
}

function MicOffIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="1" y1="1" x2="23" y2="23" />
      <path d="M9 9v3a3 3 0 0 0 5.12 2.12M15 9.34V4a3 3 0 0 0-5.94-.6" />
      <path d="M17 16.95A7 7 0 0 1 5 12v-2m14 0v2c0 .76-.13 1.49-.35 2.17" />
      <line x1="12" y1="19" x2="12" y2="23" />
      <line x1="8" y1="23" x2="16" y2="23" />
    </svg>
  );
}

function WaveIcon() {
  return (
    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
      <line x1="4" y1="8" x2="4" y2="16"><animate attributeName="y1" values="8;4;8" dur="0.8s" repeatCount="indefinite" /></line>
      <line x1="8" y1="6" x2="8" y2="18"><animate attributeName="y1" values="6;2;6" dur="0.6s" repeatCount="indefinite" /></line>
      <line x1="12" y1="4" x2="12" y2="20"><animate attributeName="y1" values="4;1;4" dur="0.7s" repeatCount="indefinite" /></line>
      <line x1="16" y1="6" x2="16" y2="18"><animate attributeName="y1" values="6;2;6" dur="0.5s" repeatCount="indefinite" /></line>
      <line x1="20" y1="8" x2="20" y2="16"><animate attributeName="y1" values="8;4;8" dur="0.9s" repeatCount="indefinite" /></line>
    </svg>
  );
}

function SpinnerIcon() {
  return (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
      <path d="M12 2a10 10 0 0 1 10 10">
        <animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="1s" repeatCount="indefinite" />
      </path>
    </svg>
  );
}

function DashIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="7" height="7" rx="1" /><rect x="14" y="3" width="7" height="7" rx="1" />
      <rect x="3" y="14" width="7" height="7" rx="1" /><rect x="14" y="14" width="7" height="7" rx="1" />
    </svg>
  );
}

const styles: Record<string, React.CSSProperties> = {
  page: { display: "flex", minHeight: "100vh", background: "#F4F5F7", fontFamily: "'Inter', system-ui, sans-serif", color: "#111827", margin: 0 },

  sidebar: { width: 220, background: "#111318", color: "#fff", display: "flex", flexDirection: "column", flexShrink: 0 },
  sidebarLogo: { padding: "20px 20px 24px", display: "flex", alignItems: "center", gap: 10, borderBottom: "1px solid rgba(255,255,255,0.08)" },
  sidebarTitle: { fontWeight: 700, fontSize: "0.95rem" },
  sidebarSection: { fontSize: "0.65rem", fontWeight: 600, textTransform: "uppercase" as const, letterSpacing: "0.08em", color: "rgba(255,255,255,0.35)", padding: "16px 20px 6px" },
  sidebarLink: { display: "flex", alignItems: "center", gap: 10, padding: "9px 20px", color: "rgba(255,255,255,0.5)", fontSize: "0.82rem", fontWeight: 500, cursor: "pointer", borderRadius: 0 },
  sidebarLinkActive: { background: "#2A2D38", color: "#fff" },
  sidebarSpacer: { flex: 1 },
  sidebarFooter: { padding: "16px 20px", borderTop: "1px solid rgba(255,255,255,0.08)", fontSize: "0.68rem", color: "rgba(255,255,255,0.25)", textAlign: "center" as const },

  main: { flex: 1, display: "flex", flexDirection: "column" as const, minHeight: "100vh" },
  topbar: { background: "#fff", borderBottom: "1px solid #E5E7EB", padding: "16px 32px", display: "flex", alignItems: "center", gap: 16 },
  topbarTitle: { fontSize: "1.05rem", fontWeight: 600 },
  topbarDivider: { width: 1, height: 20, background: "#E5E7EB" },
  topbarSub: { fontSize: "0.82rem", color: "#6B7280" },
  liveBadge: { display: "flex", alignItems: "center", gap: 8 },
  liveDot: { width: 8, height: 8, background: "#22C55E", borderRadius: "50%", animation: "pulse 2s ease-in-out infinite" },

  content: { padding: "32px", flex: 1, display: "flex", flexDirection: "column" as const, gap: 20, maxWidth: 900, margin: "0 auto", width: "100%" },

  callCard: { background: "#fff", border: "1px solid #E5E7EB", borderRadius: 12, padding: "40px 32px", textAlign: "center" as const },
  callVisual: { marginBottom: 32 },
  callCircle: { width: 80, height: 80, borderRadius: "50%", background: "#F4F5F7", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 20px", color: "#6B7280", transition: "all 0.3s" },
  callCircleActive: { background: "rgba(34,197,94,0.1)", color: "#22C55E" },
  callCirclePending: { background: "rgba(249,115,22,0.1)", color: "#F97316" },
  callStatus: { fontSize: "1.1rem", fontWeight: 600, marginBottom: 6 },
  callHint: { fontSize: "0.85rem", color: "#6B7280", maxWidth: 420, margin: "0 auto" },

  controls: { display: "flex", justifyContent: "center", gap: 12 },
  btnStart: { display: "flex", alignItems: "center", gap: 8, padding: "12px 28px", background: "#22C55E", color: "#fff", border: "none", borderRadius: 10, fontSize: "0.9rem", fontWeight: 600, cursor: "pointer" },
  btnEnd: { display: "flex", alignItems: "center", gap: 8, padding: "12px 28px", background: "#EF4444", color: "#fff", border: "none", borderRadius: 10, fontSize: "0.9rem", fontWeight: 600, cursor: "pointer" },
  btnMute: { display: "flex", alignItems: "center", gap: 8, padding: "12px 24px", background: "#fff", color: "#111827", border: "1px solid #E5E7EB", borderRadius: 10, fontSize: "0.9rem", fontWeight: 600, cursor: "pointer" },
  btnMuted: { display: "flex", alignItems: "center", gap: 8, padding: "12px 24px", background: "#FEF3C7", color: "#92400E", border: "1px solid #FDE68A", borderRadius: 10, fontSize: "0.9rem", fontWeight: 600, cursor: "pointer" },
  btnDisabled: { padding: "12px 28px", background: "#E5E7EB", color: "#9CA3AF", border: "none", borderRadius: 10, fontSize: "0.9rem", fontWeight: 600, cursor: "not-allowed" },

  logCard: { background: "#fff", border: "1px solid #E5E7EB", borderRadius: 12, overflow: "hidden", flex: 1 },
  logHeader: { display: "flex", justifyContent: "space-between", alignItems: "center", padding: "14px 20px", borderBottom: "1px solid #E5E7EB" },
  logTitle: { fontSize: "0.85rem", fontWeight: 600 },
  logCount: { fontSize: "0.75rem", color: "#9CA3AF" },
  logBody: { padding: "8px 0", maxHeight: 320, overflowY: "auto" as const },
  logEmpty: { padding: "40px 20px", textAlign: "center" as const, color: "#9CA3AF", fontSize: "0.85rem" },
  logRow: { display: "flex", alignItems: "center", gap: 10, padding: "6px 20px" },
  logTime: { fontFamily: "'JetBrains Mono', monospace", fontSize: "0.72rem", color: "#9CA3AF", flexShrink: 0, width: 80 },
  logDot: { width: 6, height: 6, borderRadius: "50%", flexShrink: 0 },
  logMsg: { fontSize: "0.82rem", color: "#374151" },
};
