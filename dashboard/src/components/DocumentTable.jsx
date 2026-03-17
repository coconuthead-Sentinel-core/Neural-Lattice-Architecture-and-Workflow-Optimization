import { useEffect, useState } from "react";
import { api } from "../api";
import CreateDocumentForm from "./CreateDocumentForm";

function LoadBar({ value }) {
  const pct = (value / 10) * 100;
  const cls = value <= 3 ? "low" : value <= 6 ? "med" : "high";
  return (
    <div className="load-bar">
      <span>{value}</span>
      <div className="load-bar-track">
        <div className={`load-bar-fill ${cls}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

export default function DocumentTable({ onRefresh }) {
  const [docs, setDocs] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [filter, setFilter] = useState("");

  const load = () => {
    api.listDocuments().then(setDocs).catch(() => {});
  };

  useEffect(() => { load(); }, []);

  const handleDelete = async (id) => {
    await api.deleteDocument(id);
    load();
    onRefresh?.();
  };

  const handleCreated = () => {
    setShowForm(false);
    load();
    onRefresh?.();
  };

  const filtered = filter
    ? docs.filter((d) => d.zone === filter)
    : docs;

  return (
    <>
      {showForm && (
        <CreateDocumentForm
          onCreated={handleCreated}
          onCancel={() => setShowForm(false)}
        />
      )}
      <div className="docs-section">
        <div className="docs-header">
          <h2>Documents ({filtered.length})</h2>
          <div style={{ display: "flex", gap: "0.5rem" }}>
            <select
              className="btn btn-sm"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
            >
              <option value="">All Zones</option>
              <option value="GREEN">GREEN</option>
              <option value="YELLOW">YELLOW</option>
              <option value="RED">RED</option>
            </select>
            <button className="btn btn-accent" onClick={() => setShowForm(!showForm)}>
              + New Document
            </button>
          </div>
        </div>
        {filtered.length === 0 ? (
          <div className="empty-state">
            <p>No documents yet.</p>
            <button className="btn" onClick={() => setShowForm(true)}>
              Create your first document
            </button>
          </div>
        ) : (
          <table className="docs-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Zone</th>
                <th>Status</th>
                <th>Load</th>
                <th>Type</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((doc) => (
                <tr key={doc.doc_id}>
                  <td><code>{doc.doc_id}</code></td>
                  <td>{doc.title}</td>
                  <td>
                    <span className={`zone-badge ${doc.zone.toLowerCase()}`}>
                      {doc.zone}
                    </span>
                  </td>
                  <td><span className="status-badge">{doc.status}</span></td>
                  <td><LoadBar value={doc.cognitive_load} /></td>
                  <td>{doc.artifact_type}</td>
                  <td>
                    <button
                      className="btn btn-sm btn-danger"
                      onClick={() => handleDelete(doc.doc_id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
