import { useEffect, useState } from "react";
import { api } from "../api";

/*
  Eisenhower Matrix mapping for Neural Lattice:

  Q1: Urgent + Important    = GREEN zone, DRAFT status (active, needs work now)
  Q2: Not Urgent + Important = GREEN zone, ACTIVE/TESTING (important but stable)
  Q3: Urgent + Not Important = YELLOW zone (synthesis, moderate priority)
  Q4: Not Urgent + Not Important = RED zone (archived, reference)
*/

function classifyQuadrant(doc) {
  if (doc.zone === "GREEN" && (doc.status === "DRAFT" || doc.cognitive_load >= 8)) {
    return "q1";
  }
  if (doc.zone === "GREEN") {
    return "q2";
  }
  if (doc.zone === "YELLOW") {
    return "q3";
  }
  return "q4";
}

const QUADRANTS = {
  q1: { title: "Do First", subtitle: "Urgent + Important" },
  q2: { title: "Schedule", subtitle: "Important, Not Urgent" },
  q3: { title: "Delegate", subtitle: "Urgent, Not Important" },
  q4: { title: "Archive", subtitle: "Not Urgent, Not Important" },
};

export default function EisenhowerMatrix() {
  const [docs, setDocs] = useState([]);

  useEffect(() => {
    api.listDocuments().then(setDocs).catch(() => {});
  }, []);

  const buckets = { q1: [], q2: [], q3: [], q4: [] };
  docs.forEach((doc) => {
    const q = classifyQuadrant(doc);
    buckets[q].push(doc);
  });

  if (docs.length === 0) {
    return (
      <div className="empty-state">
        <p>No documents to display in the matrix.</p>
        <p>Create documents in the Triage tab to populate the Eisenhower matrix.</p>
      </div>
    );
  }

  return (
    <div className="matrix-container">
      <div className="matrix-axis-labels">
        <span className="matrix-axis-label">Urgent</span>
        <span className="matrix-axis-label">Not Urgent</span>
      </div>
      <div className="matrix">
        {Object.entries(QUADRANTS).map(([key, { title, subtitle }]) => (
          <div key={key} className={`matrix-cell ${key}`}>
            <h4>{title} <span style={{ fontWeight: 400, opacity: 0.6 }}>({subtitle})</span></h4>
            {buckets[key].length === 0 ? (
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", padding: "0.5rem 0" }}>
                No items
              </div>
            ) : (
              buckets[key].map((doc) => (
                <div key={doc.doc_id} className="matrix-item">
                  <span>{doc.title}</span>
                  <span className={`zone-badge ${doc.zone.toLowerCase()}`}>
                    {doc.zone}
                  </span>
                </div>
              ))
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
