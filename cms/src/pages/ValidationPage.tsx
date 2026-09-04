import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchApi } from '../api/client';
import { ValidationReportResponse } from '../types';
import { CheckCircle2, AlertTriangle, RefreshCw } from 'lucide-react';

export const ValidationPage: React.FC = () => {
  const { data, isLoading, refetch, isRefetching } = useQuery({
    queryKey: ['validation-report'],
    queryFn: () => fetchApi<ValidationReportResponse>('/admin/validation-report'),
  });

  return (
    <div className="page-container">
      <div className="page-header flex-between">
        <div>
          <h1>Publishing Readiness Validation Report</h1>
          <p>Live audit inspecting database fields and artwork file storage prior to catalogue publishing.</p>
        </div>
        <button onClick={() => refetch()} className="btn-secondary" disabled={isRefetching}>
          <RefreshCw size={16} className={isRefetching ? 'spin' : ''} /> Run Audit
        </button>
      </div>

      {isLoading ? (
        <div className="loading-state">Running validation audit...</div>
      ) : data?.is_publishable ? (
        <div className="status-banner success">
          <CheckCircle2 size={32} />
          <div>
            <h3>All Checks Passed! Catalogue is Ready for Publishing.</h3>
            <p>Audited {data.shows_count} published shows and {data.episodes_count} published episodes. No blockers found.</p>
          </div>
        </div>
      ) : (
        <div className="status-banner warning">
          <AlertTriangle size={32} />
          <div>
            <h3>Publishing Blocked — {data?.total_blockers} Blocker(s) Found</h3>
            <p>Please resolve the metadata or artwork errors listed below before triggering a catalogue publish.</p>
          </div>
        </div>
      )}

      {/* Blockers Breakdown */}
      {data && data.shows_with_issues.length > 0 && (
        <div className="validation-report-list">
          <h2>Detailed Blocker Breakdown</h2>
          {data.shows_with_issues.map((showReport) => (
            <div key={showReport.show_id} className="validation-card">
              <h3 className="show-card-title">{showReport.show_title}</h3>
              <ul className="problem-list">
                {showReport.problems.map((prob, idx) => (
                  <li key={idx} className="problem-item">
                    <AlertTriangle size={14} className="icon-warning" />
                    <span>{prob}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
