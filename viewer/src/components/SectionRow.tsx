import React from 'react';
import { CatalogueShow } from '../types';
import { ShowCard } from './ShowCard';

interface SectionRowProps {
  title: string;
  shows: CatalogueShow[];
}

export const SectionRow: React.FC<SectionRowProps> = ({ title, shows }) => {
  if (!shows || shows.length === 0) return null;

  return (
    <section className="section-row">
      <h2 className="row-title">{title}</h2>
      <div className="row-cards-scroll">
        {shows.map((show) => (
          <ShowCard key={show.id} show={show} />
        ))}
      </div>
    </section>
  );
};
