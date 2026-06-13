export default function Loader({ error }) {
  if (error) return <div className="status error">error: {error}</div>;
  return <div className="status loading">fetching...</div>;
}
