import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  const sec = payload[0].value;
  const m = Math.floor(sec / 60);
  const s = Math.round(sec % 60);
  return (
    <div style={{ background: "#111", border: "1px solid #2e2e2e", padding: "8px 12px", fontFamily: "inherit", fontSize: 11 }}>
      <div style={{ color: "#555", marginBottom: 2 }}>{label}</div>
      <div style={{ color: "#e8e8e8" }}>{m}:{String(s).padStart(2,"0")} avg</div>
    </div>
  );
};

export default function DurationChart({ data }) {
  return (
    <div className="chart-card">
      <h2>avg duration by genre</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} margin={{ left: 0, right: 16, top: 0, bottom: 56 }}>
          <CartesianGrid strokeDasharray="2 4" vertical={false} stroke="#1e1e1e" />
          <XAxis
            dataKey="genre"
            tick={{ fill: "#555", fontSize: 9, fontFamily: "inherit", angle: -45, textAnchor: "end" }}
            interval={0}
            axisLine={false}
            tickLine={false}
          />
          <YAxis tick={{ fill: "#444", fontSize: 10, fontFamily: "inherit" }} axisLine={false} tickLine={false} />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: "#1a1a1a" }} />
          <Bar dataKey="avg_duration_sec" fill="#444" radius={0} maxBarSize={20} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
