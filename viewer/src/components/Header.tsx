import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Search } from 'lucide-react';

export const Header: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchTerm.trim())}`);
    }
  };

  return (
    <header className="viewer-header">
      <div className="header-left">
        <Link to="/" className="brand-logo">PEBLO TV</Link>
        <nav className="header-nav">
          <Link to="/">Home</Link>
          <Link to="/search?section=Trending%20Now">Trending</Link>
          <Link to="/search?category=Drama">Dramas</Link>
          <Link to="/search?category=Crime">Crime</Link>
          <Link to="/search?category=Sci-Fi">Sci-Fi</Link>
        </nav>
      </div>

      <form onSubmit={handleSearchSubmit} className="header-search">
        <Search size={16} className="search-icon" />
        <input
          type="text"
          placeholder="Titles, episodes, genres..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </form>
    </header>
  );
};
