export interface EpisodeVariant {
  language: string;
  title: string;
  duration_seconds?: number;
  thumbnail_url?: string;
}

export interface CatalogueEpisode {
  content_group: string;
  episode_number: number;
  title: string;
  synopsis?: string;
  duration_seconds?: number;
  poster_url?: string;
  banner_url?: string;
  thumbnail_url?: string;
  languages: string[];
  variants: EpisodeVariant[];
}

export interface CatalogueSeason {
  id: string;
  season_number: number;
  title: string;
  episodes: CatalogueEpisode[];
}

export interface CatalogueShow {
  id: string;
  title: string;
  synopsis?: string;
  category?: string;
  section?: string;
  poster_url?: string;
  banner_url?: string;
  seasons: CatalogueSeason[];
  trailers: CatalogueEpisode[];
}

export interface SectionGroup {
  name: string;
  shows: CatalogueShow[];
}

export interface CatalogueResponse {
  version: string;
  generated_at: string;
  total_shows: number;
  total_episodes: number;
  sections: SectionGroup[];
  shows: CatalogueShow[];
}
