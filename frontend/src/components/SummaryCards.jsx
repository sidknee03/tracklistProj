export default function SummaryCards({ data }) {
  if (!data) return null;
  const fmt = (n) => Number(n).toLocaleString();
  const usd = (n) => `$${Number(n).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  const cards = [
    { label: "total royalties",  value: usd(data.total_revenue_usd) },
    { label: "total streams",    value: fmt(data.total_streams)      },
    { label: "artists",          value: fmt(data.total_artists)      },
    { label: "platforms",        value: fmt(data.total_platforms)    },
  ];

  return (
    <div className="summary-cards">
      {cards.map(c => (
        <div className="card" key={c.label}>
          <span className="card-label">{c.label}</span>
          <span className="card-value">{c.value}</span>
        </div>
      ))}
    </div>
  );
}
