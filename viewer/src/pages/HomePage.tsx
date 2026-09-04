import React, { useEffect, useState } from 'react';
import { getPublishedCatalogue } from '../api/client';
import { CatalogueResponse } from '../types';
import { Hero } from '../components/Hero';
import { SectionRow } from '../components/SectionRow';
import { AlertCircle } from 'lucide-react';

export const HomePage: React.FC = () => {
  const [data, setData] = useState<CatalogueResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getPublishedCatalogue()
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || 'Failed to load catalogue');
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div className="viewer-loading">Loading Peblo TV catalogue...</div>;
  }

  if (error || !data) {
    return (
      <div className="viewer-empty">
        <AlertCircle size={40} className="error-icon" />
        <h2>No Published Catalogue Available</h2>
        <p>The catalogue has not been published yet from the CMS. Please log in to the CMS and trigger a publish.</p>
      </div>
    );
  }

  const heroShow = data.shows[0];

  return (
    <div className="home-page">
      {heroShow && <Hero show={heroShow} />}

      <div className="sections-container">
        {data.sections.map((section) => (
          <SectionRow key={section.name} title={section.name} shows={section.shows} />
        ))}
      </div>
    </div>
  );
};
