import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getPublishedCatalogue, formatImageUrl } from '../api/client';
import { CatalogueShow, CatalogueSeason } from '../types';
import { Play, Globe, ArrowLeft, Video } from 'lucide-react';

export const ShowDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [show, setShow] = useState<CatalogueShow | null>(null);
  const [selectedSeason, setSelectedSeason] = useState<CatalogueSeason | null>(null);
  const [selectedLanguage, setSelectedLanguage] = useState<string>('All');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getPublishedCatalogue().then((catalogue) => {
      const match = catalogue.shows.find((s) => s.id === id);
      if (match) {
        setShow(match);
        // Exclude Season 0 from normal season selector
        const normalSeasons = match.seasons.filter((s) => s.season_number > 0);
        if (normalSeasons.length > 0) {
          setSelectedSeason(normalSeasons[0]);
        }
      }
      setLoading(false);
    });
  }, [id]);

  if (loading) return <div className="viewer-loading">Loading show details...</div>;
  if (!show) return <div className="viewer-empty">Show not found in published catalogue.</div>;

  const normalSeasons = show.seasons.filter((s) => s.season_number > 0);

  // Collect all available languages across episodes
  const availableLanguages = Array.from(
    new Set(
      (selectedSeason?.episodes || []).flatMap((ep) => ep.languages)
    )
  );

  const filteredEpisodes = (selectedSeason?.episodes || []).filter((ep) => {
    if (selectedLanguage === 'All') return true;
    return ep.languages.includes(selectedLanguage);
  });

  return (
    <div className="detail-page">
      <Link to="/" className="back-link"><ArrowLeft size={16} /> Back to Home</Link>

      <div className="detail-header" style={{ backgroundImage: `url(${formatImageUrl(show.banner_url || show.poster_url)})` }}>
        <div className="detail-header-overlay">
          <div className="detail-header-content">
            <img src={formatImageUrl(show.poster_url)} alt={show.title} className="detail-poster" />
            <div className="detail-meta">
              <span className="badge">{show.category}</span>
              <h1>{show.title}</h1>
              <p className="synopsis">{show.synopsis}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Season 0 Trailers & Teasers Section */}
      {show.trailers && show.trailers.length > 0 && (
        <div className="trailers-section">
          <h2><Video size={20} /> Trailers & Teasers</h2>
          <div className="episodes-grid">
            {show.trailers.map((trailer) => (
              <div key={trailer.content_group} className="episode-card trailer">
                <div className="ep-thumb-wrapper">
                  <img src={formatImageUrl(trailer.thumbnail_url)} alt={trailer.title} className="ep-thumb" />
                </div>
                <div className="ep-info">
                  <h4>{trailer.title}</h4>
                  <p>{trailer.synopsis}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Normal Seasons Section */}
      <div className="episodes-container">
        <div className="seasons-toolbar">
          <div className="season-select-box">
            <label>Season:</label>
            <select
              value={selectedSeason?.id || ''}
              onChange={(e) => {
                const target = normalSeasons.find((s) => s.id === e.target.value);
                if (target) setSelectedSeason(target);
              }}
            >
              {normalSeasons.map((season) => (
                <option key={season.id} value={season.id}>
                  {season.title || `Season ${season.season_number}`}
                </option>
              ))}
            </select>
          </div>

          <div className="language-select-box">
            <Globe size={16} />
            <label>Language Variant:</label>
            <select
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
            >
              <option value="All">All Languages</option>
              {availableLanguages.map((lang) => (
                <option key={lang} value={lang}>{lang}</option>
              ))}
            </select>
          </div>
        </div>

        <h3 className="section-subtitle">
          {selectedSeason?.title || `Season ${selectedSeason?.season_number}`} — {filteredEpisodes.length} Episode(s)
        </h3>

        <div className="episodes-list">
          {filteredEpisodes.map((ep) => (
            <div key={ep.content_group} className="episode-row">
              <div className="ep-thumb-wrapper">
                {ep.thumbnail_url ? (
                  <img src={formatImageUrl(ep.thumbnail_url)} alt={ep.title} className="ep-thumb" />
                ) : (
                  <div className="ep-thumb-placeholder">No Thumb</div>
                )}
                <div className="play-overlay"><Play size={24} fill="#fff" /></div>
              </div>

              <div className="ep-details">
                <div className="ep-header">
                  <h4>Ep {ep.episode_number}: {ep.title}</h4>
                  {ep.duration_seconds && (
                    <span className="duration">{Math.floor(ep.duration_seconds / 60)} min</span>
                  )}
                </div>
                <p className="ep-synopsis">{ep.synopsis}</p>
                <div className="ep-langs">
                  <span className="lang-label">Available Audio/Subtitles:</span>
                  {ep.languages.map((lang) => (
                    <span key={lang} className="lang-badge">{lang}</span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
