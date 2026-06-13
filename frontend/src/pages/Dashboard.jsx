import { useQuery }        from "../hooks/useQuery";
import { fetchSummary, fetchGenres, fetchPopByDecade, fetchTopArtists, fetchDurationByGenre } from "../api";
import SummaryCards    from "../components/SummaryCards";
import GenreChart      from "../components/GenreChart";
import PopularityChart from "../components/PopularityChart";
import ArtistsChart    from "../components/ArtistsChart";
import DurationChart   from "../components/DurationChart";
import Loader          from "../components/Loader";

export default function Dashboard() {
  const summary  = useQuery(fetchSummary);
  const genres   = useQuery(fetchGenres);
  const decades  = useQuery(fetchPopByDecade);
  const artists  = useQuery(fetchTopArtists);
  const duration = useQuery(fetchDurationByGenre);

  return (
    <div className="dashboard">
      <header className="dash-header">
        <h1>music.db</h1>
        <p>spotify library · postgresql · {new Date().getFullYear()}</p>
      </header>

      {summary.loading
        ? <Loader error={summary.error} />
        : <SummaryCards data={summary.data} />}

      <div className="charts-grid">
        {genres.loading   ? <Loader error={genres.error}   /> : <GenreChart      data={genres.data}   />}
        {decades.loading  ? <Loader error={decades.error}  /> : <PopularityChart  data={decades.data}  />}
        {artists.loading  ? <Loader error={artists.error}  /> : <ArtistsChart     data={artists.data}  />}
        {duration.loading ? <Loader error={duration.error} /> : <DurationChart    data={duration.data} />}
      </div>
    </div>
  );
}
