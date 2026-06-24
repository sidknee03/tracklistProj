import axios from "axios";

const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
const api  = axios.create({ baseURL: BASE });

export const fetchSummary          = () => api.get("/api/summary").then(r => r.data);
export const fetchPlatformRevenue  = () => api.get("/api/platforms/revenue").then(r => r.data);
export const fetchTopArtists       = () => api.get("/api/artists/top").then(r => r.data);
export const fetchGenreRevenue     = () => api.get("/api/genres/revenue").then(r => r.data);
export const fetchMonthlyTrend     = () => api.get("/api/trends/monthly").then(r => r.data);
