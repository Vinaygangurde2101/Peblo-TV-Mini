import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Header } from './components/Header';
import { HomePage } from './pages/HomePage';
import { ShowDetailPage } from './pages/ShowDetailPage';
import { SearchPage } from './pages/SearchPage';

export default function App() {
  return (
    <BrowserRouter>
      <div className="viewer-layout">
        <Header />
        <main className="viewer-main">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/show/:id" element={<ShowDetailPage />} />
            <Route path="/search" element={<SearchPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
