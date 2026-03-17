import { useEffect, useState } from "react";
import { api } from "../api";

const ZONE_META = {
  GREEN: { label: "Active Development", loadRange: "7-10", css: "green" },
  YELLOW: { label: "Synthesis & Review", loadRange: "4-6", css: "yellow" },
  RED: { label: "Archived / Reference", loadRange: "1-3", css: "red" },
};

export default function ZoneOverview() {
  const [counts, setCounts] = useState({ GREEN: 0, YELLOW: 0, RED: 0 });

  useEffect(() => {
    api.zoneSummary().then(setCounts).catch(() => {});
  }, []);

  return (
    <div className="zone-grid">
      {Object.entries(ZONE_META).map(([zone, meta]) => (
        <div key={zone} className={`zone-card ${meta.css}`}>
          <h3>{zone} Zone</h3>
          <div className="zone-count">{counts[zone] || 0}</div>
          <div className="zone-label">{meta.label}</div>
          <div className="zone-load">Cognitive Load: {meta.loadRange}</div>
        </div>
      ))}
    </div>
  );
}
