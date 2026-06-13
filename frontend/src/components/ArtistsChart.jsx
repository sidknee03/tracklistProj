import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from "recharts";

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div style={{ background: "#111", border: "1px solid #2e2e2e", padding: "8px 12px", fontFamily: "inherit", fontSize: 11 }}>
      <div style={{ color: "#555", marginBottom: 2 }}>#{d.rnk} {d.name}</div>
      <div style={{ color: "#e8e8e8" }}>{d.track_count} tracks</div>
      <div style={{ color: "#444", fontSize: 10 }}>pop score {d.artist_popularity}</div>
    </div>
  );
};

export default function ArtistsChart({ data }) {
  return (
    <div className="chart-card">
      <h2>top artists — ranked by track count</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} layout="vertical" margin={{ left: 4, right: 16, top: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="2 4" horizontal={false} stroke="#1e1e1e" />
          <XAxis type="number" tick={{ fill: "#444", fontSize: 10, fontFamily: "inherit" }} axisLine={false} tickLine={false} />
          <YAxis type="category" dataKey="name" tick={{ fill: "#666", fontSize: 10, fontFamily: "inherit" }} width={110} axisLine={false} tickLine={false} />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: "#1a1a1a" }} />
          <Bar dataKey="track_count" radius={0} maxBarSize={12}>
            {data.map((_, i) => (
              <Cell key={i} fill={i === 0 ? "#e8e8e8" : i < 3 ? "#888" : "#333"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
