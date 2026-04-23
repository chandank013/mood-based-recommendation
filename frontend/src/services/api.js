import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:5000/api",
  timeout: 15000,
});

export const detectMoodText   = (data) => API.post("/mood/text",  data);
export const detectMoodEmoji  = (data) => API.post("/mood/emoji", data);
export const detectMoodFace   = (data) => API.post("/mood/face",  data);
export const detectMoodVoice  = (data) => API.post("/mood/voice", data);
export const getPassiveSignals = (city) => API.get("/mood/passive", { params: { city } });

export const getRecommendations = (data) => API.post("/recommendations", data);
export const getActivities = (emotion) => API.get("/recommendations/activities", { params: { emotion } });

export const getMoodHistory = (session_id, days = 7) =>
  API.get("/journey/history", { params: { session_id, days } });
export const getMoodSummary = (session_id) =>
  API.get("/journey/summary", { params: { session_id } });

export const getTrending    = () => API.get("/social/trending");
export const getSocialPulse = () => API.get("/social/pulse");
export const contribute     = (emotion) => API.post("/social/contribute", { emotion });
export const healthCheck    = () => API.get("/health");

export default API;