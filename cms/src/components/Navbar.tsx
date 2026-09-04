import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { UserProfile } from '../types';
import { removeAuthToken } from '../api/client';
import { LayoutDashboard, Film, FolderGit2, Tv, CheckCircle, UploadCloud, LogOut } from 'lucide-react';

interface NavbarProps {
  user: UserProfile | null;
}

export const Navbar: React.FC<NavbarProps> = ({ user }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    removeAuthToken();
    navigate('/login');
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <header className="navbar">
      <div className="nav-brand">
        <Link to="/" className="logo-link">PEBLO CMS</Link>
        {user && (
          <span className={`role-badge ${user.role}`}>
            {user.role.toUpperCase()}
          </span>
        )}
      </div>

      {user && (
        <nav className="nav-links">
          <Link to="/" className={isActive('/') ? 'active' : ''}>
            <LayoutDashboard size={16} /> Overview
          </Link>
          <Link to="/shows" className={isActive('/shows') ? 'active' : ''}>
            <Film size={16} /> Shows
          </Link>
          <Link to="/seasons" className={isActive('/seasons') ? 'active' : ''}>
            <FolderGit2 size={16} /> Seasons
          </Link>
          <Link to="/episodes" className={isActive('/episodes') ? 'active' : ''}>
            <Tv size={16} /> Episodes
          </Link>
          <Link to="/validation" className={isActive('/validation') ? 'active' : ''}>
            <CheckCircle size={16} /> Validation Report
          </Link>
          <Link to="/publish" className={isActive('/publish') ? 'active' : ''}>
            <UploadCloud size={16} /> Publish
          </Link>
        </nav>
      )}

      {user && (
        <div className="nav-user">
          <span className="user-email">{user.email}</span>
          <button onClick={handleLogout} className="btn-logout" title="Sign Out">
            <LogOut size={16} />
          </button>
        </div>
      )}
    </header>
  );
};
