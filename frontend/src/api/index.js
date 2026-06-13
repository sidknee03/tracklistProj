import axios from "axios";

const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

const api = axios.create({ baseURL: BASE });

export const fetchSummary        = () => api.get("/api/stats/summary").then(r => r.data);
export const fetchGenres         = () => api.get("/api/genres/distribution").then(r => r.data);
export const fetchPopByDecade    = () => api.get("/api/popularity/by-decade").then(r => r.data);
export const fetchTopArtists     = () => api.get("/api/artists/top").then(r => r.data);
export const fetchDurationByGenre = () => api.get("/api/duration/by-genre").then(r => r.data);
