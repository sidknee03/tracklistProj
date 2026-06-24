import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell, Legend,
} from "recharts";

const COLORS = ["#e8e8e8","#c0c0c0","#a0a0a0","#808080","#606060","#484848","#383838","#282828","#1e1e1e"];

const Tip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div style={{ background: "#111", border: "1px solid #2e2e2e", padding: "8px 12px", fontFamily: "inherit", fontSize: 11 }}>
      <div style={{ color: "#888", marginBottom: 4 }}>{d.platform} · {d.model}</div>
      <div style={{ color: "#e8e8e8" }}>${Number(d.total_revenue).toLocaleString(undefined, { maximumFractionDigits: 0 })} revenue</div>
      <div style={{ color: "#555", marginTop: 2 }}>{Number(d.total_units).toLocaleString()} units</div>
      <div style={{ color: "#555" }}>${d.rate_per_unit}/unit published</div>
    </div>
  );
};

export default function PlatformChart({ data }) {
  return (
    <div className="chart-card">
      <h2>revenue by platform</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} margin={{ left: 10, right: 16, top: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="2 4" vertical={false} stroke="#1e1e1e" />
          <XAxis dataKey="platform" tick={{ fill: "#555", fontSize: 9, fontFamily: "inherit" }} axisLine={false} tickLine={false} />
          <YAxis tickFormatter={v => `$${(v/1000).toFixed(0)}k`} tick={{ fill: "#444", fontSize: 10, fontFamily: "inherit" }} axisLine={false} tickLine={false} />
          <Tooltip content={<Tip />} cursor={{ fill: "#1a1a1a" }} />
          <Bar dataKey="total_revenue" radius={0} maxBarSize={36}>
            {data.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
