import {
  ComposedChart, Line, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from "recharts";

const Tip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: "#111", border: "1px solid #2e2e2e", padding: "8px 12px", fontFamily: "inherit", fontSize: 11 }}>
      <div style={{ color: "#888", marginBottom: 4 }}>{label}</div>
      {payload.map(p => (
        <div key={p.name} style={{ color: p.name === "running_total" ? "#e8e8e8" : "#666" }}>
          {p.name === "running_total" ? "cumulative" : "this month"}: ${Number(p.value).toLocaleString(undefined, { maximumFractionDigits: 0 })}
        </div>
      ))}
    </div>
  );
};

export default function TrendChart({ data }) {
  return (
    <div className="chart-card">
      <h2>monthly revenue + running total</h2>
      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart data={data} margin={{ left: 10, right: 16, top: 10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="2 4" stroke="#1e1e1e" />
          <XAxis dataKey="period" tick={{ fill: "#444", fontSize: 9, fontFamily: "inherit" }} axisLine={false} tickLine={false} interval={2} />
          <YAxis yAxisId="left"  tickFormatter={v => `$${(v/1000).toFixed(0)}k`} tick={{ fill: "#444", fontSize: 10, fontFamily: "inherit" }} axisLine={false} tickLine={false} />
          <YAxis yAxisId="right" orientation="right" tickFormatter={v => `$${(v/1000).toFixed(0)}k`} tick={{ fill: "#333", fontSize: 10, fontFamily: "inherit" }} axisLine={false} tickLine={false} />
          <Tooltip content={<Tip />} cursor={{ fill: "#1a1a1a" }} />
          <Bar yAxisId="left" dataKey="monthly_revenue" fill="#2e2e2e" maxBarSize={20} />
          <Line yAxisId="right" type="monotone" dataKey="running_total" stroke="#e8e8e8" strokeWidth={1.5} dot={false} />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
