import React, { useEffect, useState } from 'react';
import Viewer3D, { MeshData, LineData } from './viewer3d';

const Viewer3DExample: React.FC = () => {
  const [meshes, setMeshes] = useState<MeshData[]>([]);
  const [lines, setLines] = useState<LineData | undefined>(undefined);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Chargement des données depuis votre API
    const fetchData = async () => {
      try {
        const meshResponse = await fetch('/api/meshes');
        const meshData = await meshResponse.json();
        setMeshes(meshData);

        const lineResponse = await fetch('/api/lines');
        const lineData = await lineResponse.json();
        setLines(lineData);
      } catch (error) {
        console.error('Error loading 3D data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <Viewer3D
      width={800}
      height={600}
      meshes={meshes}
      lines={lines}
      backgroundColor={0x363432}
    />
  );
};

export default Viewer3DExample;
