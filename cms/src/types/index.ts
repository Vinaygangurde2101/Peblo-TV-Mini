export type UserRole = 'editor' | 'admin';

export interface UserProfile {
  id: string;
  email: string;
  role: UserRole;
  full_name?: string;
}

export type ContentStatus = 'draft' | 'published' | 'archived';

export interface Show {
  id: string;
  title: string;
  synopsis?: string;
  category?: string;
  section?: string;
  status: ContentStatus;
  poster_url?: string;
  banner_url?: string;
  created_at: string;
  updated_at: string;
}

export interface Season {
  id: string;
  show_id: string;
  season_number: number;
  title?: string;
  status: ContentStatus;
  created_at: string;
  updated_at: string;
}

export interface Episode {
  id: string;
  season_id: string;
  episode_number: number;
  title: string;
  synopsis?: string;
  duration_seconds?: number;
  content_group: string;
  language: string;
  status: ContentStatus;
  poster_url?: string;
  banner_url?: string;
  thumbnail_url?: string;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ShowValidationReport {
  show_id: string;
  show_title: string;
  problems: string[];
}

export interface ValidationReportResponse {
  is_publishable: boolean;
  total_blockers: number;
  shows_count: number;
  episodes_count: number;
  shows_with_issues: ShowValidationReport[];
}

export interface PublishRun {
  id: string;
  published_by_user_id?: string;
  status: 'success' | 'failed';
  show_count: number;
  episode_count: number;
  validation_errors?: any;
  snapshot_path?: string;
  error_message?: string;
  created_at: string;
}
