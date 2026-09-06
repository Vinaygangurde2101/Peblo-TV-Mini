import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchApi } from '../api/client';
import { Episode, PaginatedResponse, ContentStatus } from '../types';
import { ArtworkUpload } from '../components/ArtworkUpload';
import { Plus, Search, Edit2, Trash2, X } from 'lucide-react';

export const EpisodesPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [seasonFilter, setSeasonFilter] = useState('');
  const [languageFilter, setLanguageFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingEp, setEditingEp] = useState<Episode | null>(null);
  const [formData, setFormData] = useState({
    season_id: '',
    episode_number: 1,
    title: '',
    synopsis: '',
    duration_seconds: 3000,
    content_group: '',
    language: 'English',
    status: 'draft' as ContentStatus,
    thumbnail_url: '',
  });

  // Fetch Seasons & Shows for dropdowns
  const { data: seasonsData } = useQuery({
    queryKey: ['admin-seasons'],
    queryFn: () => fetchApi<any[]>('/admin/seasons'),
  });

  const { data: showsData } = useQuery({
    queryKey: ['admin-shows-all'],
    queryFn: () => fetchApi<PaginatedResponse<any>>('/admin/shows?page_size=100'),
  });

  const showsMap = React.useMemo(() => {
    const map = new Map<string, string>();
    showsData?.items.forEach((s) => map.set(s.id, s.title));
    return map;
  }, [showsData]);

  const { data, isLoading } = useQuery({
    queryKey: ['episodes', page, search, seasonFilter, languageFilter, statusFilter],
    queryFn: () => {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: '10',
      });
      if (search) params.append('q', search);
      if (seasonFilter) params.append('season_id', seasonFilter);
      if (languageFilter) params.append('language', languageFilter);
      if (statusFilter) params.append('status', statusFilter);
      return fetchApi<PaginatedResponse<Episode>>(`/admin/episodes?${params.toString()}`);
    },
  });

  const saveMutation = useMutation({
    mutationFn: (payload: any) => {
      if (editingEp) {
        return fetchApi<Episode>(`/admin/episodes/${editingEp.id}`, {
          method: 'PUT',
          body: JSON.stringify(payload),
        });
      }
      return fetchApi<Episode>('/admin/episodes', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['episodes'] });
      closeModal();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (epId: string) =>
      fetchApi(`/admin/episodes/${epId}`, { method: 'DELETE' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['episodes'] });
    },
  });

  const openCreateModal = () => {
    setEditingEp(null);
    const defaultSeasonId = seasonsData && seasonsData.length > 0 ? seasonsData[0].id : '';
    setFormData({
      season_id: defaultSeasonId,
      episode_number: 1,
      title: '',
      synopsis: '',
      duration_seconds: 3000,
      content_group: `ep-${Date.now().toString().slice(-4)}`,
      language: 'English',
      status: 'draft',
      thumbnail_url: '',
    });
    setIsModalOpen(true);
  };

  const openEditModal = (ep: Episode) => {
    setEditingEp(ep);
    setFormData({
      season_id: ep.season_id,
      episode_number: ep.episode_number,
      title: ep.title,
      synopsis: ep.synopsis || '',
      duration_seconds: ep.duration_seconds || 0,
      content_group: ep.content_group,
      language: ep.language,
      status: ep.status,
      thumbnail_url: ep.thumbnail_url || '',
    });
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingEp(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.season_id) {
      alert('Please select or create a season first.');
      return;
    }
    saveMutation.mutate(formData);
  };

  return (
    <div className="page-container">
      <div className="page-header flex-between">
        <div>
          <h1>Episode Management</h1>
          <p>Manage episode variants, durations, multi-language groupings, and thumbnails.</p>
        </div>
        <button onClick={openCreateModal} className="btn-primary">
          <Plus size={16} /> Add Episode
        </button>
      </div>

      <div className="filter-bar">
        <div className="search-box">
          <Search size={16} />
          <input
            type="text"
            placeholder="Search episodes..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          />
        </div>

        <select value={seasonFilter} onChange={(e) => { setSeasonFilter(e.target.value); setPage(1); }}>
          <option value="">All Seasons</option>
          {seasonsData?.map((s) => {
            const showTitle = showsMap.get(s.show_id) || 'Show';
            return (
              <option key={s.id} value={s.id}>
                {showTitle} — {s.season_number === 0 ? 'Trailers (S0)' : `Season ${s.season_number}`}
              </option>
            );
          })}
        </select>

        <select value={languageFilter} onChange={(e) => { setLanguageFilter(e.target.value); setPage(1); }}>
          <option value="">All Languages</option>
          <option value="English">English</option>
          <option value="Hindi">Hindi</option>
          <option value="Spanish">Spanish</option>
          <option value="Tamil">Tamil</option>
          <option value="Marathi">Marathi</option>
        </select>

        <select value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}>
          <option value="">All Statuses</option>
          <option value="draft">Draft</option>
          <option value="published">Published</option>
        </select>
      </div>

      {isLoading ? (
        <div className="loading-state">Loading episodes...</div>
      ) : data?.items.length === 0 ? (
        <div className="empty-state">No episodes found.</div>
      ) : (
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Thumbnail</th>
                <th>Title</th>
                <th>Content Group</th>
                <th>Language</th>
                <th>Duration</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {data?.items.map((ep) => (
                <tr key={ep.id}>
                  <td>
                    {ep.thumbnail_url ? (
                      <img
                        src={ep.thumbnail_url.startsWith('http') ? ep.thumbnail_url : `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${ep.thumbnail_url}`}
                        alt={ep.title}
                        className="table-thumb"
                      />
                    ) : (
                      <div className="no-img">No Thumb</div>
                    )}
                  </td>
                  <td>
                    <strong>Ep {ep.episode_number}: {ep.title}</strong>
                  </td>
                  <td><code>{ep.content_group}</code></td>
                  <td><span className="lang-tag">{ep.language}</span></td>
                  <td>{ep.duration_seconds ? `${Math.floor(ep.duration_seconds / 60)}m` : <span className="warning-text">Missing</span>}</td>
                  <td>
                    <span className={`status-pill ${ep.status}`}>{ep.status.toUpperCase()}</span>
                  </td>
                  <td>
                    <button onClick={() => openEditModal(ep)} className="btn-icon" title="Edit"><Edit2 size={16} /></button>
                    <button
                      onClick={() => { if (confirm(`Delete episode '${ep.title}'?`)) deleteMutation.mutate(ep.id); }}
                      className="btn-icon danger"
                      title="Delete"
                    >
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal */}
      {isModalOpen && (
        <div className="modal-backdrop">
          <div className="modal-content">
            <div className="modal-header">
              <h2>{editingEp ? 'Edit Episode' : 'Create Episode'}</h2>
              <button onClick={closeModal} className="btn-icon"><X size={18} /></button>
            </div>

            <form onSubmit={handleSubmit} className="modal-form">
              <div className="form-group">
                <label>Parent Season / Show *</label>
                <select
                  value={formData.season_id}
                  onChange={(e) => setFormData({ ...formData, season_id: e.target.value })}
                  required
                >
                  <option value="">Select Season...</option>
                  {seasonsData?.map((s) => {
                    const showTitle = showsMap.get(s.show_id) || 'Show';
                    return (
                      <option key={s.id} value={s.id}>
                        {showTitle} — {s.season_number === 0 ? 'Trailers & Teasers (S0)' : (s.title || `Season ${s.season_number}`)}
                      </option>
                    );
                  })}
                </select>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Episode Number</label>
                  <input
                    type="number"
                    value={formData.episode_number}
                    onChange={(e) => setFormData({ ...formData, episode_number: parseInt(e.target.value) })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Language Variant</label>
                  <select
                    value={formData.language}
                    onChange={(e) => setFormData({ ...formData, language: e.target.value })}
                  >
                    <option value="English">English</option>
                    <option value="Hindi">Hindi</option>
                    <option value="Spanish">Spanish</option>
                    <option value="Tamil">Tamil</option>
                    <option value="Marathi">Marathi</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label>Episode Title *</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  required
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Content Group Key (Links Multi-Language Variants)</label>
                  <input
                    type="text"
                    value={formData.content_group}
                    onChange={(e) => setFormData({ ...formData, content_group: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Duration (Seconds)</label>
                  <input
                    type="number"
                    value={formData.duration_seconds}
                    onChange={(e) => setFormData({ ...formData, duration_seconds: parseInt(e.target.value) })}
                  />
                </div>
                <div className="form-group">
                  <label>Content Status</label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value as ContentStatus })}
                  >
                    <option value="draft">Draft</option>
                    <option value="published">Published</option>
                  </select>
                </div>
              </div>

              <div className="artwork-grid">
                <ArtworkUpload
                  artworkType="thumbnail"
                  currentUrl={formData.thumbnail_url}
                  onUploadSuccess={(url) => setFormData({ ...formData, thumbnail_url: url })}
                />
              </div>

              <div className="modal-actions">
                <button type="button" onClick={closeModal} className="btn-secondary">Cancel</button>
                <button type="submit" className="btn-primary" disabled={saveMutation.isPending}>
                  {saveMutation.isPending ? 'Saving...' : 'Save Episode'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
