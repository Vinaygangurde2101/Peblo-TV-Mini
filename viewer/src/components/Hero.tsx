import React from 'react';
import { Link } from 'react-router-dom';
import { CatalogueShow } from '../types';
import { formatImageUrl } from '../api/client';
import { Play, Info } from 'lucide-react';

interface HeroProps {
  show: CatalogueShow;
}

export const Hero: React.FC<HeroProps> = ({ show }) => {
  const bannerUrl = formatImageUrl(show.banner_url || show.poster_url);

  return (
    <div className="hero-banner" style={{ backgroundImage: `url(${bannerUrl})` }}>
      <div className="hero-overlay">
        <div className="hero-content">
          <span className="hero-badge">{show.category || 'Featured'}</span>
          <h1 className="hero-title">{show.title}</h1>
          <p className="hero-synopsis">{show.synopsis}</p>

          <div className="hero-actions">
            <Link to={`/show/${show.id}`} className="btn-hero-play">
              <Play size={18} fill="currentColor" /> Watch Now
            </Link>
            <Link to={`/show/${show.id}`} className="btn-hero-info">
              <Info size={18} /> More Info
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
