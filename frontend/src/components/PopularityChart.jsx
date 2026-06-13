import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine,
} from "recharts";

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: "#111", border: "1px solid #2e2e2e", padding: "8px 12px", fontFamily: "inherit", fontSize: 11 }}>
      <div style={{ color: "#555", marginBottom: 2 }}>{label}s</div>
      <div style={{ color: "#e8e8e8" }}>avg {payload[0].value}</div>
      <div style={{ color: "#444", fontSize: 10 }}>{payload[0].payload.track_count} tracks</div>
    </div>
  );
};

export default function PopularityChart({ data }) {
  return (
    <div className="chart-card">
      <h2>popularity by decade</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} margin={{ left: 0, right: 16, top: 10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="2 4" stroke="#1e1e1e" />
          <XAxis
            dataKey="decade"
            tickFormatter={v => `'${String(v).slice(2)}`}
            tick={{ fill: "#444", fontSize: 10, fontFamily: "inherit" }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis domain={[0, 100]} tick={{ fill: "#444", fontSize: 10, fontFamily: "inherit" }} axisLine={false} tickLine={false} />
          <ReferenceLine y={50} stroke="#2a2a2a" strokeDasharray="3 3" />
          <Tooltip content={<CustomTooltip />} cursor={{ stroke: "#2e2e2e" }} />
          <Line
            type="monotone"
            dataKey="avg_popularity"
            stroke="#e8e8e8"
            strokeWidth={1.5}
            dot={{ fill: "#0a0a0a", stroke: "#e8e8e8", r: 3, strokeWidth: 1.5 }}
            activeDot={{ fill: "#e8e8e8", r: 4, strokeWidth: 0 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
