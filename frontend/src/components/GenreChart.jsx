import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";

const SHADES = ["#e8e8e8","#c8c8c8","#a8a8a8","#888","#686868","#505050","#404040","#333","#282828","#222"];

const Tip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div style={{ background: "#111", border: "1px solid #2e2e2e", padding: "8px 12px", fontFamily: "inherit", fontSize: 11 }}>
      <div style={{ color: "#888", marginBottom: 4 }}>{d.genre}</div>
      <div style={{ color: "#e8e8e8" }}>${Number(d.total_revenue).toLocaleString(undefined, { maximumFractionDigits: 0 })}</div>
      <div style={{ color: "#555" }}>{d.artist_count} artists · {d.track_count} tracks</div>
    </div>
  );
};

export default function GenreChart({ data }) {
  return (
    <div className="chart-card">
      <h2>revenue by genre</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} margin={{ left: 10, right: 16, top: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="2 4" vertical={false} stroke="#1e1e1e" />
          <XAxis dataKey="genre" tick={{ fill: "#555", fontSize: 9, fontFamily: "inherit" }} axisLine={false} tickLine={false} />
          <YAxis tickFormatter={v => `$${(v/1000).toFixed(0)}k`} tick={{ fill: "#444", fontSize: 10, fontFamily: "inherit" }} axisLine={false} tickLine={false} />
          <Tooltip content={<Tip />} cursor={{ fill: "#1a1a1a" }} />
          <Bar dataKey="total_revenue" radius={0} maxBarSize={32}>
            {data.map((_, i) => <Cell key={i} fill={SHADES[i % SHADES.length]} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
