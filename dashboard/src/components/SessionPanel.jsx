import { useState } from "react";
import { api } from "../api";

export default function SessionPanel() {
  const [session, setSession] = useState(null);
  const [loadInput, setLoadInput] = useState(5);
  const [error, setError] = useState("");

  const handle = (fn) => async () => {
    setError("");
    try {
      const result = await fn();
      setSession(result);
    } catch (err) {
      setError(err.message);
    }
  };

  if (!session) {
    return (
      <div className="session-panel">
        <h3>Session Manager</h3>
        <p style={{ margin: "1rem 0", color: "var(--text-muted)" }}>
          Start a Pomodoro session to track cognitive load and enforce breaks.
        </p>
        {error && (
          <div className="error-banner">
            {error}
            <button onClick={() => setError("")}>x</button>
          </div>
        )}
        <button className="btn btn-accent" onClick={handle(() => api.createSession())}>
          Start New Session
        </button>
      </div>
    );
  }

  const phase = session.phase;
  const canWork = ["INIT", "BREAK", "LONG_BREAK"].includes(phase);
  const canEndWork = phase === "WORK";
  const canWrapUp = !["CLOSED", "WRAP_UP"].includes(phase);
  const canClose = phase === "WRAP_UP";

  return (
    <div className="session-panel">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h3>Session: {session.session_id?.slice(0, 8)}...</h3>
        <span className="status-badge">{phase}</span>
      </div>

      {error && (
        <div className="error-banner">
          {error}
          <button onClick={() => setError("")}>x</button>
        </div>
      )}

      <div className="session-info">
        <div className="session-stat">
          <div className="value">{session.pomodoro_count}</div>
          <div className="label">Pomodoros</div>
        </div>
        <div className="session-stat">
          <div className="value">
            {session.average_cognitive_load != null
              ? session.average_cognitive_load.toFixed(1)
              : "--"}
          </div>
          <div className="label">Avg Load</div>
        </div>
        <div className="session-stat">
          <div className="value">{session.work_blocks?.length || 0}</div>
          <div className="label">Work Blocks</div>
        </div>
        <div className="session-stat">
          <div className="value">{session.pomodoro_minutes}m</div>
          <div className="label">Pomodoro</div>
        </div>
      </div>

      <div className="session-actions">
        {canWork && (
          <button
            className="btn btn-accent"
            onClick={handle(() => api.startWork(session.session_id))}
          >
            Start Work Block
          </button>
        )}
        {canEndWork && (
          <>
            <div className="form-group" style={{ flexDirection: "row", alignItems: "center", gap: "0.5rem" }}>
              <label style={{ fontSize: "0.8rem" }}>Load:</label>
              <input
                type="number"
                min="1"
                max="10"
                value={loadInput}
                onChange={(e) => setLoadInput(Number(e.target.value))}
                style={{
                  width: "60px",
                  padding: "0.3rem",
                  borderRadius: "6px",
                  border: "1px solid var(--border)",
                  background: "var(--bg)",
                  color: "var(--text)",
                }}
              />
            </div>
            <button
              className="btn"
              onClick={handle(() =>
                api.endWork(session.session_id, { cognitive_load: loadInput })
              )}
            >
              End Work Block
            </button>
          </>
        )}
        {canWrapUp && (
          <button
            className="btn"
            onClick={handle(() => api.wrapUp(session.session_id))}
          >
            Wrap Up
          </button>
        )}
        {canClose && (
          <button
            className="btn"
            onClick={handle(() => api.closeSession(session.session_id))}
          >
            Close Session
          </button>
        )}
        {phase === "CLOSED" && (
          <button
            className="btn btn-accent"
            onClick={() => setSession(null)}
          >
            New Session
          </button>
        )}
      </div>
    </div>
  );
}
