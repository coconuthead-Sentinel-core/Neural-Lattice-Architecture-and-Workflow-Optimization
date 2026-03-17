import { useState, useEffect, useCallback } from "react";
import { api } from "./api";
import ZoneOverview from "./components/ZoneOverview";
import DocumentTable from "./components/DocumentTable";
import EisenhowerMatrix from "./components/EisenhowerMatrix";
import SessionPanel from "./components/SessionPanel";

function App() {
  const [tab, setTab] = useState("overview");
  const [online, setOnline] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  const refresh = useCallback(() => setRefreshKey((k) => k + 1), []);

  useEffect(() => {
    api.health().then(() => setOnline(true)).catch(() => setOnline(false));
  }, []);

  return (
    <div className="app">
      <header className="header">
        <h1>Neural Lattice Dashboard</h1>
        <div className="status">
          <span className={`status-dot ${online ? "" : "offline"}`} />
          <span>{online ? "API Connected" : "API Offline"}</span>
        </div>
      </header>

      <nav className="tabs">
        {[
          ["overview", "Zone Overview"],
          ["triage", "Document Triage"],
          ["matrix", "Eisenhower Matrix"],
          ["session", "Session"],
        ].map(([key, label]) => (
          <button
            key={key}
            className={`tab ${tab === key ? "active" : ""}`}
            onClick={() => setTab(key)}
          >
            {label}
          </button>
        ))}
      </nav>

      <main className="main" key={refreshKey}>
        {tab === "overview" && (
          <>
            <ZoneOverview />
            <DocumentTable onRefresh={refresh} />
          </>
        )}
        {tab === "triage" && <DocumentTable onRefresh={refresh} />}
        {tab === "matrix" && <EisenhowerMatrix />}
        {tab === "session" && <SessionPanel />}
      </main>
    </div>
  );
}

export default App;
