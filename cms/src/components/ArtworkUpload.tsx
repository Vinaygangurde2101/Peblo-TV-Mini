import React, { useState } from 'react';
import { fetchApi } from '../api/client';
import { Upload, AlertTriangle, Image as ImageIcon } from 'lucide-react';

interface ArtworkUploadProps {
  artworkType: 'poster' | 'banner' | 'thumbnail';
  currentUrl?: string;
  onUploadSuccess: (url: string) => void;
}

export const ArtworkUpload: React.FC<ArtworkUploadProps> = ({
  artworkType,
  currentUrl,
  onUploadSuccess,
}) => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | undefined>(currentUrl);

  const getSpecs = () => {
    switch (artworkType) {
      case 'poster':
        return { dims: '~600 x 900 px', ratio: '2:3' };
      case 'banner':
        return { dims: '1280 x 720 px', ratio: '16:9' };
      case 'thumbnail':
        return { dims: '640 x 360 px', ratio: '16:9' };
    }
  };

  const specs = getSpecs();

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Client-side quick size check
    if (file.size > 200 * 1024) {
      setError(`File size exceeds 200 KB limit. Uploaded size: ${(file.size / 1024).toFixed(1)} KB.`);
      return;
    }

    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('artwork_type', artworkType);
    formData.append('file', file);

    try {
      const res = await fetchApi<{ url: string }>(`/admin/artwork/upload`, {
        method: 'POST',
        body: formData,
      });

      const fullUrl = res.url.startsWith('http') ? res.url : `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${res.url}`;
      setPreviewUrl(fullUrl);
      onUploadSuccess(res.url);
    } catch (err: any) {
      setError(err.message || 'Artwork upload failed validation.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="artwork-upload-box">
      <div className="artwork-meta">
        <span className="artwork-title">{artworkType.toUpperCase()}</span>
        <span className="artwork-spec">Target: {specs.dims} ({specs.ratio}) • Max: 200 KB</span>
      </div>

      <div className="artwork-preview-area">
        {previewUrl ? (
          <img src={previewUrl} alt={`${artworkType} preview`} className={`preview-img ${artworkType}`} />
        ) : (
          <div className="placeholder">
            <ImageIcon size={32} />
            <span>No {artworkType} uploaded</span>
          </div>
        )}
      </div>

      <label className={`upload-btn ${uploading ? 'disabled' : ''}`}>
        <Upload size={16} />
        {uploading ? 'Validating...' : `Upload ${artworkType}`}
        <input type="file" accept="image/jpeg,image/png,image/webp" onChange={handleFileChange} disabled={uploading} hidden />
      </label>

      {error && (
        <div className="error-callout">
          <AlertTriangle size={16} />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
};
