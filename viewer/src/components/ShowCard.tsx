import React from 'react';
import { Link } from 'react-router-dom';
import { CatalogueShow } from '../types';
import { formatImageUrl } from '../api/client';

interface ShowCardProps {
  show: CatalogueShow;
}

export const ShowCard: React.FC<ShowCardProps> = ({ show }) => {
  const posterUrl = formatImageUrl(show.poster_url);

  return (
    <Link to={`/show/${show.id}`} className="show-card">
      <div className="card-poster-wrapper">
        {posterUrl ? (
          <img src={posterUrl} alt={show.title} className="card-poster" loading="lazy" />
        ) : (
          <div className="card-poster-placeholder">
            <span>{show.title}</span>
          </div>
        )}
      </div>
      <div className="card-info">
        <span className="card-title">{show.title}</span>
        <span className="card-meta">{show.category}</span>
      </div>
    </Link>
  );
};
