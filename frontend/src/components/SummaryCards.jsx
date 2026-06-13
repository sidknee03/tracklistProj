export default function SummaryCards({ data }) {
  if (!data) return null;
  const cards = [
    { label: "tracks in library", value: data.total_tracks  },
    { label: "unique artists",    value: data.total_artists },
    { label: "genres mapped",     value: data.total_genres  },
  ];
  return (
    <div className="summary-cards">
      {cards.map(c => (
        <div className="card" key={c.label}>
          <span className="card-label">{c.label}</span>
          <span className="card-value">{c.value?.toLocaleString()}</span>
        </div>
      ))}
    </div>
  );
}
