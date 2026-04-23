import { useState, useCallback, useRef } from "react";
import { getRecommendations } from "../services/api.js";

export function useRecommendations() {
  const [recs,    setRecs]    = useState(null);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState(null);
  const lastKeyRef = useRef(null); // track last fetch key to avoid duplicate fetches

  const fetch = useCallback(async (moodLogId, emotion, mode = "amplify") => {
    if (!moodLogId || !emotion) return;

    // Build a cache key — different mode must always re-fetch
    const key = `${moodLogId}-${emotion}-${mode}`;
    if (key === lastKeyRef.current && recs) return; // skip if same request already loaded

    lastKeyRef.current = key;
    setRecs(null);     // clear previous results to show shimmer
    setLoading(true);
    setError(null);

    try {
      const { data } = await getRecommendations({ mood_log_id: moodLogId, emotion, mode });
      // Only update if this is still the latest request
      if (lastKeyRef.current === key) {
        setRecs(data);
      }
      return data;
    } catch (e) {
      setError(e?.response?.data?.error || "Failed to fetch recommendations");
    } finally {
      setLoading(false);
    }
  }, [recs]);

  const clear = useCallback(() => {
    setRecs(null);
    setError(null);
    lastKeyRef.current = null;
  }, []);

  return { recs, loading, error, fetch, clear };
}