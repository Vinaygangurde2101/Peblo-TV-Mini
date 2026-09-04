import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchApi } from '../api/client';
import { ValidationReportResponse, PublishRun, UserProfile } from '../types';
import { UploadCloud, History, Lock } from 'lucide-react';

interface PublishPageProps {
  user: UserProfile | null;
}

export const PublishPage: React.FC<PublishPageProps> = ({ user }) => {
  const queryClient = useQueryClient();
  const [publishMessage, setPublishMessage] = useState<string | null>(null);

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
      queryClient.invalidateQueries({ queryKey: ['publish-history'] });
      queryClient.invalidateQueries({ queryKey: ['validation-report'] });
    },
    onError: (err: any) => {
      setPublishMessage(err.message || 'Publishing failed.');
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

        <button
          onClick={() => publishMutation.mutate()}
          disabled={isPublishDisabled}
          className={`btn-publish ${isPublishDisabled ? 'disabled' : ''}`}
        >
          <UploadCloud size={20} />
          {publishMutation.isPending ? 'Publishing Catalogue...' : 'Publish Catalogue Now'}
        </button>
      </div>

      {/* Publish History */}
      <div className="history-section">
        <h2><History size={20} /> Publish Audit History</h2>
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
