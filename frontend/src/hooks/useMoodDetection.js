import { useState, useCallback } from "react";
import { detectMoodText, detectMoodEmoji, detectMoodFace, detectMoodVoice, contribute } from "../services/api";

const SESSION_KEY = "moodly_session";

function getSessionId() {
  try {
    let sid = localStorage.getItem(SESSION_KEY);
    if (!sid) {
      sid = `sess_${Date.now()}_${Math.random().toString(36).slice(2)}`;
      localStorage.setItem(SESSION_KEY, sid);
    }
    return sid;
  } catch {
    return `sess_${Date.now()}`;
  }
}

export function useMoodDetection() {
  const [sessionId,  setSessionId]  = useState(() => getSessionId());
  const [emotion,    setEmotion]    = useState(null);
  const [confidence, setConfidence] = useState(null);
  const [allScores,  setAllScores]  = useState({});
  const [moodLogId,  setMoodLogId]  = useState(null);
  const [loading,    setLoading]    = useState(false);
  const [error,      setError]      = useState(null);

  const _handleResult = useCallback((data) => {
    setEmotion(data.emotion);
    setConfidence(data.confidence);
    setAllScores(data.all_scores || {});
    setMoodLogId(data.mood_log_id);
    contribute(data.emotion).catch(() => {});
    return data;
  }, []);

  const fromText = useCallback(async (text, mode = "amplify", contextWho = null) => {
    if (!text?.trim()) return null;
    setLoading(true); setError(null);
    try {
      const { data } = await detectMoodText({
        text,
        session_id:  sessionId,
        mode,
        context_who: contextWho,
      });
      return _handleResult(data);
    } catch (e) {
      setError(e?.response?.data?.error || "Failed to detect mood. Is the backend running?");
      return null;
    } finally {
      setLoading(false);
    }
  }, [sessionId, _handleResult]);

  const fromEmoji = useCallback(async (emoji, slider, mode = "amplify") => {
    setLoading(true); setError(null);
    try {
      const { data } = await detectMoodEmoji({ emoji, slider, session_id: sessionId, mode });
      return _handleResult(data);
    } catch (e) {
      setError(e?.response?.data?.error || "Failed to detect mood.");
      return null;
    } finally {
      setLoading(false);
    }
  }, [sessionId, _handleResult]);

  const fromFace = useCallback(async (imageB64, mode = "amplify") => {
    setLoading(true); setError(null);
    try {
      const { data } = await detectMoodFace({ image: imageB64, session_id: sessionId, mode });
      return _handleResult(data);
    } catch (e) {
      setError(e?.response?.data?.error || "Face analysis failed.");
      return null;
    } finally {
      setLoading(false);
    }
  }, [sessionId, _handleResult]);

  const fromVoice = useCallback(async (audioB64, mode = "amplify") => {
    setLoading(true); setError(null);
    try {
      const { data } = await detectMoodVoice({ audio: audioB64, session_id: sessionId, mode });
      return _handleResult(data);
    } catch (e) {
      setError(e?.response?.data?.error || "Voice analysis failed.");
      return null;
    } finally {
      setLoading(false);
    }
  }, [sessionId, _handleResult]);

  const reset = useCallback(() => {
    setEmotion(null); setConfidence(null);
    setAllScores({}); setMoodLogId(null); setError(null);
  }, []);

  return {
    sessionId, emotion, confidence, allScores, moodLogId,
    loading, error,
    fromText, fromEmoji, fromFace, fromVoice, reset,
  };
}