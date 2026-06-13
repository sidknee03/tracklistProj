import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from "recharts";

const PALETTE = ["#e8e8e8","#c8c8c8","#a8a8a8","#888888","#686868","#505050","#404040","#333333"];

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: "#111", border: "1px solid #2e2e2e", padding: "8px 12px", fontFamily: "inherit", fontSize: 11 }}>
      <div style={{ color: "#555", marginBottom: 2 }}>{label}</div>
      <div style={{ color: "#e8e8e8" }}>{payload[0].value} tracks</div>
    </div>
  );
};

export default function GenreChart({ data }) {
  return (
    <div className="chart-card">
      <h2>genre distribution</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} layout="vertical" margin={{ left: 4, right: 16, top: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="2 4" horizontal={false} stroke="#1e1e1e" />
          <XAxis type="number" tick={{ fill: "#444", fontSize: 10, fontFamily: "inherit" }} axisLine={false} tickLine={false} />
          <YAxis type="category" dataKey="genre" tick={{ fill: "#666", fontSize: 10, fontFamily: "inherit" }} width={90} axisLine={false} tickLine={false} />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: "#1a1a1a" }} />
          <Bar dataKey="track_count" radius={0} maxBarSize={14}>
            {data.map((_, i) => <Cell key={i} fill={PALETTE[i % PALETTE.length]} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
