import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchApi } from '../api/client';
import { ValidationReportResponse, PublishRun, UserProfile } from '../types';
import { UploadCloud, History, Lock, RotateCcw, Eye } from 'lucide-react';

interface PublishPageProps {
  user: UserProfile | null;
}

interface DryRunDiff {
  is_publishable: boolean;
  added_shows: string[];
  modified_shows: string[];
  removed_shows: string[];
  total_shows_candidate: number;
  total_episodes_candidate: number;
  validation_blockers_count: number;
}

export const PublishPage: React.FC<PublishPageProps> = ({ user }) => {
  const queryClient = useQueryClient();
  const [publishMessage, setPublishMessage] = useState<string | null>(null);
  const [dryRunData, setDryRunData] = useState<DryRunDiff | null>(null);

  const isAdmin = user?.role === 'admin';

  const { data: validationData } = useQuery({
    queryKey: ['validation-report'],
    queryFn: () => fetchApi<ValidationReportResponse>('/admin/validation-report'),
  });

  const { data: historyData, isLoading: historyLoading } = useQuery({
    queryKey: ['publish-history'],
    queryFn: () => fetchApi<PublishRun[]>('/admin/publish-runs'),
  });

  const publishMutation = useMutation({
    mutationFn: () => fetchApi<{ message: string }>('/admin/catalog/publish', { method: 'POST' }),
    onSuccess: (data) => {
      setPublishMessage(data.message);
      setDryRunData(null);
      queryClient.invalidateQueries({ queryKey: ['publish-history'] });
      queryClient.invalidateQueries({ queryKey: ['validation-report'] });
    },
    onError: (err: any) => {
      setPublishMessage(err.message || 'Publishing failed.');
    },
  });

  const dryRunMutation = useMutation({
    mutationFn: () => fetchApi<DryRunDiff>('/admin/catalog/publish/dry-run', { method: 'POST' }),
    onSuccess: (data) => {
      setDryRunData(data);
    },
  });

  const rollbackMutation = useMutation({
    mutationFn: (runId: string) => fetchApi<{ message: string }>(`/admin/catalog/rollback/${runId}`, { method: 'POST' }),
    onSuccess: (data) => {
      setPublishMessage(data.message);
      queryClient.invalidateQueries({ queryKey: ['publish-history'] });
    },
    onError: (err: any) => {
      setPublishMessage(err.message || 'Rollback failed.');
    },
  });

  const isPublishDisabled = !isAdmin || !validationData?.is_publishable || publishMutation.isPending;

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Catalogue Publishing Engine</h1>
        <p>Trigger atomic builds of catalogue.json for consumption by the public Viewer app.</p>
      </div>

      {/* Permission Callout for Editors */}
      {!isAdmin && (
        <div className="permission-denied-banner">
          <Lock size={24} />
          <div>
            <h3>Permission Restricted</h3>
            <p>Your account role is <strong>EDITOR</strong>. Catalogue publication requires <strong>ADMIN</strong> permissions.</p>
          </div>
        </div>
      )}

      {/* Control Box */}
      <div className="publish-control-box">
        <div className="publish-status">
          <h3>Publishing Status</h3>
          <p>
            {validationData?.is_publishable
              ? 'Database state is valid and ready for publishing.'
              : `${validationData?.total_blockers ?? 0} publish blockers present.`}
          </p>
        </div>

        {publishMessage && (
          <div className="publish-message-box">{publishMessage}</div>
        )}

        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', marginTop: '16px' }}>
          <button
            onClick={() => publishMutation.mutate()}
            disabled={isPublishDisabled}
            className={`btn-publish ${isPublishDisabled ? 'disabled' : ''}`}
          >
            <UploadCloud size={20} />
            {publishMutation.isPending ? 'Publishing Catalogue...' : 'Publish Catalogue Now'}
          </button>

          <button
            onClick={() => dryRunMutation.mutate()}
            disabled={dryRunMutation.isPending}
            className="btn-secondary"
            style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 18px', borderRadius: '8px', cursor: 'pointer', backgroundColor: '#334155', color: '#fff', border: 'none' }}
          >
            <Eye size={18} />
            {dryRunMutation.isPending ? 'Calculating Diff...' : 'Preview Diff (Dry Run)'}
          </button>
        </div>
      </div>

      {/* Dry Run Preview Box */}
      {dryRunData && (
        <div style={{ backgroundColor: '#1e293b', border: '1px solid #475569', borderRadius: '12px', padding: '20px', marginBottom: '24px' }}>
          <h3 style={{ marginTop: 0, display: 'flex', alignItems: 'center', gap: '8px', color: '#38bdf8' }}>
            <Eye size={20} /> Dry Run Diff Preview
          </h3>
          <p style={{ fontSize: '14px', color: '#94a3b8' }}>
            Candidate build includes <strong>{dryRunData.total_shows_candidate}</strong> shows and <strong>{dryRunData.total_episodes_candidate}</strong> episodes.
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', marginTop: '12px' }}>
            <div style={{ backgroundColor: '#064e3b', padding: '12px', borderRadius: '8px' }}>
              <h4 style={{ margin: 0, color: '#34d399' }}>➕ Added Shows ({dryRunData.added_shows.length})</h4>
              <p style={{ margin: '4px 0 0', fontSize: '13px' }}>{dryRunData.added_shows.join(', ') || 'None'}</p>
            </div>
            <div style={{ backgroundColor: '#78350f', padding: '12px', borderRadius: '8px' }}>
              <h4 style={{ margin: 0, color: '#fbbf24' }}>✏️ Modified Shows ({dryRunData.modified_shows.length})</h4>
              <p style={{ margin: '4px 0 0', fontSize: '13px' }}>{dryRunData.modified_shows.join(', ') || 'None'}</p>
            </div>
            <div style={{ backgroundColor: '#7f1d1d', padding: '12px', borderRadius: '8px' }}>
              <h4 style={{ margin: 0, color: '#f87171' }}>🗑️ Removed Shows ({dryRunData.removed_shows.length})</h4>
              <p style={{ margin: '4px 0 0', fontSize: '13px' }}>{dryRunData.removed_shows.join(', ') || 'None'}</p>
            </div>
          </div>
        </div>
      )}

      {/* Publish History */}
      <div className="history-section">
        <h2><History size={20} /> Publish Audit History & Rollback</h2>
        {historyLoading ? (
          <div className="loading-state">Loading history...</div>
        ) : historyData?.length === 0 ? (
          <div className="empty-state">No publishing runs recorded yet.</div>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Run ID</th>
                  <th>Status</th>
                  <th>Shows</th>
                  <th>Episodes</th>
                  <th>Published At</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {historyData?.map((run) => (
                  <tr key={run.id}>
                    <td><code>{run.id.slice(0, 8)}</code></td>
                    <td>
                      <span className={`status-pill ${run.status}`}>
                        {run.status.toUpperCase()}
                      </span>
                    </td>
                    <td>{run.show_count}</td>
                    <td>{run.episode_count}</td>
                    <td>{new Date(run.created_at).toLocaleString()}</td>
                    <td>
                      {isAdmin && run.status === 'success' ? (
                        <button
                          onClick={() => rollbackMutation.mutate(run.id)}
                          disabled={rollbackMutation.isPending}
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '4px',
                            padding: '4px 10px',
                            fontSize: '12px',
                            borderRadius: '6px',
                            backgroundColor: '#475569',
                            color: '#fff',
                            border: 'none',
                            cursor: 'pointer'
                          }}
                        >
                          <RotateCcw size={12} />
                          Rollback
                        </button>
                      ) : (
                        <span style={{ fontSize: '12px', color: '#64748b' }}>N/A</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
