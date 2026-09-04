import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchApi } from '../api/client';
import { Show, PaginatedResponse, ContentStatus } from '../types';
import { ArtworkUpload } from '../components/ArtworkUpload';
import { Plus, Search, Edit2, Trash2, X } from 'lucide-react';

export const ShowsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [sectionFilter, setSectionFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingShow, setEditingShow] = useState<Show | null>(null);
  const [formData, setFormData] = useState({
    title: '',
    synopsis: '',
    category: 'Drama',
    section: 'Trending Now',
    status: 'draft' as ContentStatus,
    poster_url: '',
    banner_url: '',
  });

  const { data, isLoading } = useQuery({
    queryKey: ['shows', page, search, categoryFilter, sectionFilter, statusFilter],
    queryFn: () => {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: '8',
      });
      if (search) params.append('q', search);
      if (categoryFilter) params.append('category', categoryFilter);
      if (sectionFilter) params.append('section', sectionFilter);
      if (statusFilter) params.append('status', statusFilter);
      return fetchApi<PaginatedResponse<Show>>(`/admin/shows?${params.toString()}`);
    },
  });

  const saveMutation = useMutation({
    mutationFn: (payload: any) => {
      if (editingShow) {
        return fetchApi<Show>(`/admin/shows/${editingShow.id}`, {
          method: 'PUT',
          body: JSON.stringify(payload),
        });
      }
      return fetchApi<Show>('/admin/shows', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shows'] });
      closeModal();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (showId: string) =>
      fetchApi(`/admin/shows/${showId}`, { method: 'DELETE' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shows'] });
    },
  });

  const openCreateModal = () => {
    setEditingShow(null);
    setFormData({
      title: '',
      synopsis: '',
      category: 'Drama',
      section: 'Trending Now',
      status: 'draft',
      poster_url: '',
      banner_url: '',
    });
    setIsModalOpen(true);
  };

  const openEditModal = (show: Show) => {
    setEditingShow(show);
    setFormData({
      title: show.title,
      synopsis: show.synopsis || '',
      category: show.category || 'Drama',
      section: show.section || 'Trending Now',
      status: show.status,
      poster_url: show.poster_url || '',
      banner_url: show.banner_url || '',
    });
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingShow(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    saveMutation.mutate(formData);
  };

  return (
    <div className="page-container">
      <div className="page-header flex-between">
        <div>
          <h1>Show Management</h1>
          <p>Create and manage television series and movies.</p>
        </div>
        <button onClick={openCreateModal} className="btn-primary">
          <Plus size={16} /> Add New Show
        </button>
      </div>

      {/* Filters Toolbar */}
      <div className="filter-bar">
        <div className="search-box">
          <Search size={16} />
          <input
            type="text"
            placeholder="Search shows by title..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          />
        </div>

        <select value={categoryFilter} onChange={(e) => { setCategoryFilter(e.target.value); setPage(1); }}>
          <option value="">All Categories</option>
          <option value="Drama">Drama</option>
          <option value="Crime">Crime</option>
          <option value="Action">Action</option>
          <option value="Sci-Fi">Sci-Fi</option>
          <option value="Comedy">Comedy</option>
        </select>

        <select value={sectionFilter} onChange={(e) => { setSectionFilter(e.target.value); setPage(1); }}>
          <option value="">All Sections</option>
          <option value="Trending Now">Trending Now</option>
          <option value="Popular Dramas">Popular Dramas</option>
          <option value="Crime Chronicles">Crime Chronicles</option>
          <option value="Top Rated">Top Rated</option>
          <option value="New Releases">New Releases</option>
        </select>

        <select value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}>
          <option value="">All Statuses</option>
          <option value="draft">Draft</option>
          <option value="published">Published</option>
        </select>
      </div>

      {/* Shows List Table */}
      {isLoading ? (
        <div className="loading-state">Loading shows...</div>
      ) : data?.items.length === 0 ? (
        <div className="empty-state">No shows found matching filters.</div>
      ) : (
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Poster</th>
                <th>Title</th>
                <th>Category</th>
                <th>Section</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {data?.items.map((show) => (
                <tr key={show.id}>
                  <td>
                    {show.poster_url ? (
                      <img
                        src={show.poster_url.startsWith('http') ? show.poster_url : `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${show.poster_url}`}
                        alt={show.title}
                        className="table-poster"
                      />
                    ) : (
                      <div className="no-img">No Poster</div>
                    )}
                  </td>
                  <td>
                    <strong>{show.title}</strong>
                    <p className="table-sub">{show.synopsis?.slice(0, 60)}...</p>
                  </td>
                  <td>{show.category || '—'}</td>
                  <td>{show.section || '—'}</td>
                  <td>
                    <span className={`status-pill ${show.status}`}>
                      {show.status.toUpperCase()}
                    </span>
                  </td>
                  <td>
                    <button onClick={() => openEditModal(show)} className="btn-icon" title="Edit">
                      <Edit2 size={16} />
                    </button>
                    <button
                      onClick={() => {
                        if (confirm(`Delete '${show.title}'?`)) deleteMutation.mutate(show.id);
                      }}
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
              <h2>{editingShow ? 'Edit Show' : 'Create New Show'}</h2>
              <button onClick={closeModal} className="btn-icon"><X size={18} /></button>
            </div>

            <form onSubmit={handleSubmit} className="modal-form">
              <div className="form-group">
                <label>Show Title *</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label>Synopsis</label>
                <textarea
                  rows={3}
                  value={formData.synopsis}
                  onChange={(e) => setFormData({ ...formData, synopsis: e.target.value })}
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Category</label>
                  <select
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  >
                    <option value="Drama">Drama</option>
                    <option value="Crime">Crime</option>
                    <option value="Action">Action</option>
                    <option value="Sci-Fi">Sci-Fi</option>
                    <option value="Comedy">Comedy</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Section</label>
                  <select
                    value={formData.section}
                    onChange={(e) => setFormData({ ...formData, section: e.target.value })}
                  >
                    <option value="Trending Now">Trending Now</option>
                    <option value="Popular Dramas">Popular Dramas</option>
                    <option value="Crime Chronicles">Crime Chronicles</option>
                    <option value="Top Rated">Top Rated</option>
                    <option value="New Releases">New Releases</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Status</label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value as ContentStatus })}
                  >
                    <option value="draft">Draft</option>
                    <option value="published">Published</option>
                  </select>
                </div>
              </div>

              {/* Artwork Upload Slots */}
              <div className="artwork-grid">
                <ArtworkUpload
                  artworkType="poster"
                  currentUrl={formData.poster_url}
                  onUploadSuccess={(url) => setFormData({ ...formData, poster_url: url })}
                />
                <ArtworkUpload
                  artworkType="banner"
                  currentUrl={formData.banner_url}
                  onUploadSuccess={(url) => setFormData({ ...formData, banner_url: url })}
                />
              </div>

              <div className="modal-actions">
                <button type="button" onClick={closeModal} className="btn-secondary">Cancel</button>
                <button type="submit" className="btn-primary" disabled={saveMutation.isPending}>
                  {saveMutation.isPending ? 'Saving...' : 'Save Show'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
