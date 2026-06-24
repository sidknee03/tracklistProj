import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";

const Tip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div style={{ background: "#111", border: "1px solid #2e2e2e", padding: "8px 12px", fontFamily: "inherit", fontSize: 11 }}>
      <div style={{ color: "#888", marginBottom: 4 }}>#{d.rnk} · {d.name} · {d.country}</div>
      <div style={{ color: "#e8e8e8" }}>${Number(d.total_revenue).toLocaleString(undefined, { maximumFractionDigits: 2 })} earned</div>
      <div style={{ color: "#555" }}>{Number(d.total_units).toLocaleString()} streams</div>
    </div>
  );
};

export default function ArtistsChart({ data }) {
  return (
    <div className="chart-card">
      <h2>top artists by royalty earnings</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} layout="vertical" margin={{ left: 4, right: 16, top: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="2 4" horizontal={false} stroke="#1e1e1e" />
          <XAxis type="number" tickFormatter={v => `$${(v/1000).toFixed(1)}k`} tick={{ fill: "#444", fontSize: 10, fontFamily: "inherit" }} axisLine={false} tickLine={false} />
          <YAxis type="category" dataKey="name" width={110} tick={{ fill: "#666", fontSize: 10, fontFamily: "inherit" }} axisLine={false} tickLine={false} />
          <Tooltip content={<Tip />} cursor={{ fill: "#1a1a1a" }} />
          <Bar dataKey="total_revenue" radius={0} maxBarSize={12}>
            {data.map((_, i) => <Cell key={i} fill={i === 0 ? "#e8e8e8" : i < 3 ? "#888" : "#333"} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
