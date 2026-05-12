import type { Attraction, Itinerary, OptimizeRequest } from './types';

// Vite proxies /api → http://localhost:8000 in dev
const BASE = '/api';

export async function fetchDatasets(): Promise<string[]> {
  const res = await fetch(`${BASE}/datasets`);
  if (!res.ok) throw new Error('Failed to fetch datasets');
  return res.json();
}

export async function fetchDataset(name: string): Promise<Attraction[]> {
  const res = await fetch(`${BASE}/datasets/${name}`);
  if (!res.ok) throw new Error(`Failed to fetch dataset: ${name}`);
  return res.json();
}

export async function optimize(req: OptimizeRequest): Promise<Itinerary> {
  const res = await fetch(`${BASE}/optimize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.json();
}
