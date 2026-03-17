import { useState } from "react";
import { api } from "../api";

const DEFAULTS = {
  doc_id: "",
  title: "",
  cognitive_load: 8,
  artifact_type: "note",
  protocol: "Onset_Omega_1",
  status: "DRAFT",
  tags: "",
  content: "",
};

export default function CreateDocumentForm({ onCreated, onCancel }) {
  const [form, setForm] = useState(DEFAULTS);
  const [error, setError] = useState("");

  const set = (field) => (e) =>
    setForm((prev) => ({ ...prev, [field]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.createDocument({
        ...form,
        cognitive_load: Number(form.cognitive_load),
        tags: form.tags
          ? form.tags.split(",").map((t) => t.trim()).filter(Boolean)
          : [],
        dependencies: [],
      });
      onCreated();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <form className="create-form" onSubmit={handleSubmit}>
      <h3>Create Document</h3>
      {error && (
        <div className="error-banner">
          {error}
          <button type="button" onClick={() => setError("")}>x</button>
        </div>
      )}
      <div className="form-grid">
        <div className="form-group">
          <label>Doc ID</label>
          <input
            value={form.doc_id}
            onChange={set("doc_id")}
            placeholder="NLCA-DOC-001"
            required
          />
        </div>
        <div className="form-group">
          <label>Title</label>
          <input
            value={form.title}
            onChange={set("title")}
            placeholder="Document title"
            required
          />
        </div>
        <div className="form-group">
          <label>Cognitive Load (1-10)</label>
          <input
            type="number"
            min="1"
            max="10"
            value={form.cognitive_load}
            onChange={set("cognitive_load")}
            required
          />
        </div>
        <div className="form-group">
          <label>Artifact Type</label>
          <select value={form.artifact_type} onChange={set("artifact_type")}>
            <option value="note">Note</option>
            <option value="charter">Charter</option>
            <option value="spec">Spec</option>
            <option value="user_story">User Story</option>
            <option value="design">Design</option>
            <option value="code">Code</option>
            <option value="test">Test</option>
            <option value="runbook">Runbook</option>
            <option value="report">Report</option>
            <option value="template">Template</option>
            <option value="log">Log</option>
            <option value="config">Config</option>
          </select>
        </div>
        <div className="form-group">
          <label>Protocol</label>
          <select value={form.protocol} onChange={set("protocol")}>
            <option value="Onset_Omega_1">Onset Omega 1</option>
            <option value="Joy_Protocol">Joy Protocol</option>
            <option value="Coconut_Head">Coconut Head</option>
            <option value="Combined">Combined</option>
          </select>
        </div>
        <div className="form-group">
          <label>Tags (comma-separated)</label>
          <input
            value={form.tags}
            onChange={set("tags")}
            placeholder="design, api"
          />
        </div>
      </div>
      <div className="form-actions">
        <button type="submit" className="btn btn-accent">Create</button>
        <button type="button" className="btn" onClick={onCancel}>Cancel</button>
      </div>
    </form>
  );
}
