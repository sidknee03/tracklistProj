import { useQuery }     from "../hooks/useQuery";
import { fetchSummary, fetchPlatformRevenue, fetchTopArtists, fetchGenreRevenue, fetchMonthlyTrend } from "../api";
import SummaryCards  from "../components/SummaryCards";
import PlatformChart from "../components/PlatformChart";
import TrendChart    from "../components/TrendChart";
import ArtistsChart  from "../components/ArtistsChart";
import GenreChart    from "../components/GenreChart";
import Loader        from "../components/Loader";

export default function Dashboard() {
  const summary   = useQuery(fetchSummary);
  const platforms = useQuery(fetchPlatformRevenue);
  const artists   = useQuery(fetchTopArtists);
  const genres    = useQuery(fetchGenreRevenue);
  const trend     = useQuery(fetchMonthlyTrend);

  return (
    <div className="dashboard">
      <header className="dash-header">
        <h1>royalty.db</h1>
        <p>streaming revenue analytics · spotify · tidal · bandcamp · soundcloud + more</p>
      </header>

      {summary.loading
        ? <Loader error={summary.error} />
        : <SummaryCards data={summary.data} />}

      <div className="charts-grid">
        {platforms.loading ? <Loader error={platforms.error} /> : <PlatformChart data={platforms.data} />}
        {trend.loading     ? <Loader error={trend.error}     /> : <TrendChart    data={trend.data}     />}
        {artists.loading   ? <Loader error={artists.error}   /> : <ArtistsChart  data={artists.data}   />}
        {genres.loading    ? <Loader error={genres.error}    /> : <GenreChart    data={genres.data}    />}
      </div>
    </div>
  );
}
