import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { searchPublishedCatalogue } from '../api/client';
import { CatalogueShow } from '../types';
import { ShowCard } from '../components/ShowCard';
import { Search } from 'lucide-react';

export const SearchPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const qParam = searchParams.get('q') || '';
  const categoryParam = searchParams.get('category') || '';
  const languageParam = searchParams.get('language') || '';
  const sectionParam = searchParams.get('section') || '';

  const [shows, setShows] = useState<CatalogueShow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    searchPublishedCatalogue({
      q: qParam,
      category: categoryParam,
      language: languageParam,
      section: sectionParam,
    })
      .then((res) => {
        setShows(res);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [qParam, categoryParam, languageParam, sectionParam]);

  const updateFilter = (key: string, value: string) => {
    const newParams = new URLSearchParams(searchParams);
    if (value) {
      newParams.set(key, value);
    } else {
      newParams.delete(key);
    }
    setSearchParams(newParams);
  };

  return (
    <div className="search-page">
      <div className="search-header">
        <h1>Browse Catalogue</h1>
        <p>Explore titles by genre, audio language, and featured sections.</p>
      </div>

      <div className="viewer-filter-bar">
        <div className="search-input-wrapper">
          <Search size={16} />
          <input
            type="text"
            placeholder="Search titles or episodes..."
            value={qParam}
            onChange={(e) => updateFilter('q', e.target.value)}
          />
        </div>

        <select value={categoryParam} onChange={(e) => updateFilter('category', e.target.value)}>
          <option value="">All Categories</option>
          <option value="Drama">Drama</option>
          <option value="Crime">Crime</option>
          <option value="Action">Action</option>
          <option value="Sci-Fi">Sci-Fi</option>
          <option value="Comedy">Comedy</option>
        </select>

        <select value={languageParam} onChange={(e) => updateFilter('language', e.target.value)}>
          <option value="">All Languages</option>
          <option value="English">English</option>
          <option value="Hindi">Hindi</option>
          <option value="Spanish">Spanish</option>
          <option value="Tamil">Tamil</option>
          <option value="Marathi">Marathi</option>
        </select>

        <select value={sectionParam} onChange={(e) => updateFilter('section', e.target.value)}>
          <option value="">All Sections</option>
          <option value="Trending Now">Trending Now</option>
          <option value="Popular Dramas">Popular Dramas</option>
          <option value="Crime Chronicles">Crime Chronicles</option>
          <option value="Top Rated">Top Rated</option>
          <option value="New Releases">New Releases</option>
        </select>
      </div>

      {loading ? (
        <div className="viewer-loading">Searching catalogue...</div>
      ) : shows.length === 0 ? (
        <div className="viewer-empty">
          <h2>No Shows Found</h2>
          <p>No published titles match your search criteria. Try clearing filters.</p>
        </div>
      ) : (
        <div className="shows-grid">
          {shows.map((show) => (
            <ShowCard key={show.id} show={show} />
          ))}
        </div>
      )}
    </div>
  );
};
