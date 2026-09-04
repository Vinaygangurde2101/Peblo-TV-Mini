import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fetchApi, getAuthToken } from './api/client';
import { UserProfile } from './types';
import { Navbar } from './components/Navbar';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { ShowsPage } from './pages/ShowsPage';
import { SeasonsPage } from './pages/SeasonsPage';
import { EpisodesPage } from './pages/EpisodesPage';
import { ValidationPage } from './pages/ValidationPage';
import { PublishPage } from './pages/PublishPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

export default function App() {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  const loadProfile = async () => {
    const token = getAuthToken();
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const profile = await fetchApi<UserProfile>('/auth/me');
      setUser(profile);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProfile();
  }, []);

  if (loading) {
    return <div className="loading-screen">Initializing Peblo CMS...</div>;
  }

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="app-layout">
          <Navbar user={user} />
          <main className="main-body">
            <Routes>
              <Route
                path="/login"
                element={user ? <Navigate to="/" /> : <LoginPage onLoginSuccess={loadProfile} />}
              />
              <Route
                path="/"
                element={user ? <DashboardPage /> : <Navigate to="/login" />}
              />
              <Route
                path="/shows"
                element={user ? <ShowsPage /> : <Navigate to="/login" />}
              />
              <Route
                path="/seasons"
                element={user ? <SeasonsPage /> : <Navigate to="/login" />}
              />
              <Route
                path="/episodes"
                element={user ? <EpisodesPage /> : <Navigate to="/login" />}
              />
              <Route
                path="/validation"
                element={user ? <ValidationPage /> : <Navigate to="/login" />}
              />
              <Route
                path="/publish"
                element={user ? <PublishPage user={user} /> : <Navigate to="/login" />}
              />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
