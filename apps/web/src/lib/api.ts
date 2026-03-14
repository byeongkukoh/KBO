import type { GameDetail, PlayerSummary } from "../types/game";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api").replace(/\/$/, "");

async function requestJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with ${response.status}`);
  }

  return (await response.json()) as T;
}

export function getGameDetail(gameId: string): Promise<GameDetail> {
  return requestJson<GameDetail>(`/games/${encodeURIComponent(gameId)}`);
}

export function getPlayerSummary(playerKey: string): Promise<PlayerSummary> {
  return requestJson<PlayerSummary>(`/players/${encodeURIComponent(playerKey)}/summary?scope=ingested`);
}
