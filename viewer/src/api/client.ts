import { CatalogueResponse, CatalogueShow } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function getPublishedCatalogue(): Promise<CatalogueResponse> {
  const res = await fetch(`${API_BASE_URL}/catalog`);
  if (!res.ok) {
    throw new Error('Failed to load published catalogue');
  }
  return res.json();
}

export async function searchPublishedCatalogue(params: {
  q?: string;
  category?: string;
  language?: string;
  section?: string;
}): Promise<CatalogueShow[]> {
  const query = new URLSearchParams();
  if (params.q) query.append('q', params.q);
  if (params.category) query.append('category', params.category);
  if (params.language) query.append('language', params.language);
  if (params.section) query.append('section', params.section);

  const res = await fetch(`${API_BASE_URL}/catalog/search?${query.toString()}`);
  if (!res.ok) {
    throw new Error('Failed to perform search');
  }
  return res.json();
}

export function formatImageUrl(path?: string): string {
  if (!path) return '';
  if (path.startsWith('http')) return path;
  return `${API_BASE_URL}${path}`;
}
