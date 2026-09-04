import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchApi } from '../api/client';
import { Season, Show, PaginatedResponse, ContentStatus } from '../types';
import { Plus, Edit2, Trash2, X } from 'lucide-react';

export const SeasonsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [showFilter, setShowFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingSeason, setEditingSeason] = useState<Season | null>(null);
  const [formData, setFormData] = useState({
    show_id: '',
    season_number: 1,
    title: '',
    status: 'draft' as ContentStatus,
  });

  const { data: showsData } = useQuery({
    queryKey: ['admin-shows-all'],
    queryFn: () => fetchApi<PaginatedResponse<Show>>('/admin/shows?page_size=100'),
  });

  const showsMap = React.useMemo(() => {
    const map = new Map<string, string>();
    showsData?.items.forEach((s) => map.set(s.id, s.title));
    return map;
  }, [showsData]);

  const { data: seasonsData, isLoading } = useQuery({
    queryKey: ['admin-seasons', showFilter],
    queryFn: () => {
      const url = showFilter ? `/admin/seasons?show_id=${showFilter}` : '/admin/seasons';
      return fetchApi<Season[]>(url);
    },
  });

  const saveMutation = useMutation({
    mutationFn: (payload: any) => {
      if (editingSeason) {
        return fetchApi<Season>(`/admin/seasons/${editingSeason.id}`, {
          method: 'PUT',
          body: JSON.stringify({
            season_number: payload.season_number,
            title: payload.title,
            status: payload.status,
          }),
        });
      }
      return fetchApi<Season>('/admin/seasons', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-seasons'] });
      closeModal();
    },
    onError: (err: any) => {
      alert(err.message || 'Failed to save season.');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (seasonId: string) =>
      fetchApi(`/admin/seasons/${seasonId}`, { method: 'DELETE' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-seasons'] });
    },
  });

  const openCreateModal = () => {
    setEditingSeason(null);
    const defaultShowId = showsData?.items && showsData.items.length > 0 ? showsData.items[0].id : '';
    setFormData({
      show_id: defaultShowId,
      season_number: 1,
      title: 'Season 1',
      status: 'draft',
    });
    setIsModalOpen(true);
  };

  const openEditModal = (season: Season) => {
    setEditingSeason(season);
    setFormData({
      show_id: season.show_id,
      season_number: season.season_number,
      title: season.title || '',
      status: season.status,
    });
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingSeason(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.show_id) {
      alert('Please select a show first.');
      return;
    }
    saveMutation.mutate(formData);
  };

  const filteredSeasons = React.useMemo(() => {
    if (!seasonsData) return [];
    return seasonsData.filter((s) => {
      if (statusFilter && s.status !== statusFilter) return false;
      return true;
    });
  }, [seasonsData, statusFilter]);

  return (
    <div className="page-container">
      <div className="page-header flex-between">
        <div>
          <h1>Season Management</h1>
          <p>Create and manage television seasons, including Season 0 for Trailers & Teasers.</p>
        </div>
        <button onClick={openCreateModal} className="btn-primary">
          <Plus size={16} /> Add Season
        </button>
      </div>

      <div className="filter-bar">
        <select value={showFilter} onChange={(e) => setShowFilter(e.target.value)}>
          <option value="">All Shows</option>
          {showsData?.items.map((s) => (
            <option key={s.id} value={s.id}>{s.title}</option>
          ))}
        </select>

        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="">All Statuses</option>
          <option value="draft">Draft</option>
          <option value="published">Published</option>
        </select>
      </div>

      {isLoading ? (
        <div className="loading-state">Loading seasons...</div>
      ) : filteredSeasons.length === 0 ? (
        <div className="empty-state">No seasons found.</div>
      ) : (
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Show</th>
                <th>Season Number</th>
                <th>Title</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredSeasons.map((s) => (
                <tr key={s.id}>
                  <td><strong>{showsMap.get(s.show_id) || 'Unknown Show'}</strong></td>
                  <td>
                    {s.season_number === 0 ? (
                      <span className="lang-tag" style={{ background: '#3b82f6' }}>Season 0 (Trailers)</span>
                    ) : (
                      `Season ${s.season_number}`
                    )}
                  </td>
                  <td>{s.title || `Season ${s.season_number}`}</td>
                  <td>
                    <span className={`status-pill ${s.status}`}>{s.status.toUpperCase()}</span>
                  </td>
                  <td>
                    <button onClick={() => openEditModal(s)} className="btn-icon" title="Edit"><Edit2 size={16} /></button>
                    <button
                      onClick={() => { if (confirm(`Delete season '${s.title}'?`)) deleteMutation.mutate(s.id); }}
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
              <h2>{editingSeason ? 'Edit Season' : 'Create Season'}</h2>
              <button onClick={closeModal} className="btn-icon"><X size={18} /></button>
            </div>

            <form onSubmit={handleSubmit} className="modal-form">
              {!editingSeason && (
                <div className="form-group">
                  <label>Parent Show *</label>
                  <select
                    value={formData.show_id}
                    onChange={(e) => setFormData({ ...formData, show_id: e.target.value })}
                    required
                  >
                    <option value="">Select Show...</option>
                    {showsData?.items.map((s) => (
                      <option key={s.id} value={s.id}>{s.title}</option>
                    ))}
                  </select>
                </div>
              )}

              <div className="form-row">
                <div className="form-group">
                  <label>Season Number * (Set to 0 for Trailers)</label>
                  <input
                    type="number"
                    value={formData.season_number}
                    onChange={(e) => {
                      const val = parseInt(e.target.value);
                      setFormData({
                        ...formData,
                        season_number: val,
                        title: val === 0 ? 'Trailers & Teasers' : `Season ${val}`,
                      });
                    }}
                    required
                  />
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

              <div className="form-group">
                <label>Season Title</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="e.g. Season 1 or Trailers & Teasers"
                />
              </div>

              <div className="modal-actions">
                <button type="button" onClick={closeModal} className="btn-secondary">Cancel</button>
                <button type="submit" className="btn-primary" disabled={saveMutation.isPending}>
                  {saveMutation.isPending ? 'Saving...' : 'Save Season'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
