import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchApi } from '../api/client';
import { PaginatedResponse, Show, Episode, ValidationReportResponse } from '../types';
import { Film, Tv, CheckCircle, AlertTriangle, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export const DashboardPage: React.FC = () => {
  const { data: showsData } = useQuery({
    queryKey: ['shows-count'],
    queryFn: () => fetchApi<PaginatedResponse<Show>>('/admin/shows?page_size=1'),
  });

  const { data: episodesData } = useQuery({
    queryKey: ['episodes-count'],
    queryFn: () => fetchApi<PaginatedResponse<Episode>>('/admin/episodes?page_size=1'),
  });

  const { data: validationData } = useQuery({
    queryKey: ['validation-summary'],
    queryFn: () => fetchApi<ValidationReportResponse>('/admin/validation-report'),
  });

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Editorial Dashboard</h1>
        <p>Overview of live content, publishing readiness, and metadata state.</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <Film size={28} className="stat-icon" />
          <div className="stat-info">
            <span className="stat-value">{showsData?.total ?? 0}</span>
            <span className="stat-label">Total Shows</span>
          </div>
        </div>

        <div className="stat-card">
          <Tv size={28} className="stat-icon" />
          <div className="stat-info">
            <span className="stat-value">{episodesData?.total ?? 0}</span>
            <span className="stat-label">Total Episodes</span>
          </div>
        </div>

        <div className={`stat-card ${validationData?.is_publishable ? 'success' : 'warning'}`}>
          {validationData?.is_publishable ? <CheckCircle size={28} /> : <AlertTriangle size={28} />}
          <div className="stat-info">
            <span className="stat-value">
              {validationData?.is_publishable ? 'Ready' : `${validationData?.total_blockers ?? 0} Blockers`}
            </span>
            <span className="stat-label">Publish Readiness</span>
          </div>
        </div>
      </div>

      <div className="dashboard-actions">
        <div className="action-card">
          <h3>Shows Management</h3>
          <p>Create and update shows, assign categories and target sections.</p>
          <Link to="/shows" className="btn-link">Go to Shows <ArrowRight size={16} /></Link>
        </div>

        <div className="action-card">
          <h3>Validation Audit</h3>
          <p>Inspect database metadata and artwork requirements before publishing.</p>
          <Link to="/validation" className="btn-link">Check Validation <ArrowRight size={16} /></Link>
        </div>

        <div className="action-card">
          <h3>Publishing Engine</h3>
          <p>Execute atomic snapshot builds to update the live public catalogue.</p>
          <Link to="/publish" className="btn-link">Publish Catalogue <ArrowRight size={16} /></Link>
        </div>
      </div>
    </div>
  );
};
