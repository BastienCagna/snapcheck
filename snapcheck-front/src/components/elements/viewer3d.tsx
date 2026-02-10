// import React, { useRef, useEffect } from 'react';
// import { Canvas, useThree } from '@react-three/fiber';
// import { OrbitControls } from '@react-three/drei';


// interface MeshData {
//   vertices: number[][];
//   triangles: number[][];
//   metadata?: {
//     transformations?: string;
//     name?: string;
//     [key: string]: any;
//   };
// }

// interface LineData {
//   lines: number[][][];
// }

// interface MeshProps {
//   vertices: number[][];
//   triangles: number[][];
//   metadata?: MeshData['metadata'];
//   color?: number;
//   selectable?: boolean;
//   transparent?: boolean;
// }

// interface LineProps {
//   line: number[][];
//   color?: number;
//   transparent?: boolean;
// }

// interface Viewer3DProps {
//   width?: number;
//   height?: number;
//   meshes?: MeshData[];
//   lines?: LineData;
//   backgroundColor?: number;
// }

// const Mesh3D: React.FC<MeshProps> = ({
//   vertices,
//   triangles,
//   metadata = null,
//   color = 0xaaaaaa,
//   selectable = true,
//   transparent = true,
// }) => {
//   const meshRef = useRef<Mesh>(null);

//   useEffect(() => {
//     if (!meshRef.current) return;

//     const flip = [-1, 1, 1];
//     let offset = [0, 0, 0];

//     if (metadata && metadata.transformations) {
//       const transfos = JSON.parse(metadata.transformations);
//       if (transfos.length > 1) {
//         console.log('/!\\ More than one transformation available for the mesh. Using the first.');
//       }
//       const tf = transfos[0];
//       offset = [tf[3], tf[7], tf[11]];
//     }

//     const flatVertices: number[] = [];
//     for (let v = 0; v < vertices.length; v++) {
//       for (let i = 0; i < 3; i++) {
//         flatVertices.push(flip[i] * (vertices[v][i] - offset[i]));
//       }
//     }

//     const flatTri: number[] = [];
//     for (let v = 0; v < triangles.length; v++) {
//       for (let i = 0; i < 3; i++) {
//         flatTri.push(triangles[v][i]);
//       }
//     }

//     const geometry = meshRef.current.geometry;
//     geometry.setIndex(Array.from(flatTri));
//     geometry.setAttribute('position', new THREE.Float32BufferAttribute(flatVertices, 3));
//     geometry.computeVertexNormals();
//     geometry.computeBoundingSphere();

//     if (metadata) {
//       meshRef.current.userData = metadata;
//       if (metadata.name) {
//         meshRef.current.name = metadata.name;
//       }
//     }
//   }, [vertices, triangles, metadata]);

//   return (
//     <mesh
//       ref={meshRef}
//       castShadow
//       receiveShadow
//       rotation={[0, -Math.PI / 2, Math.PI / 2]}
//     >
//       <bufferGeometry />
//       <meshStandardMaterial
//         color={color}
//         opacity={0.5}
//         transparent={transparent}
//         side={THREE.DoubleSide}
//         roughness={0.7}
//         metalness={0.4}
//       />
//     </mesh>
//   );
// };

// const Line3D: React.FC<LineProps> = ({
//   line,
//   color = 0xaaaaaa,
//   transparent = true,
// }) => {
//   const linePoints = line.map((pt) => new THREE.Vector3(pt[0], pt[1], pt[2]));

//   return (
//     <line rotation={[0, -Math.PI / 2, -Math.PI / 2]}>
//       <bufferGeometry>
//         <bufferAttribute
//           attach="attributes-position"
//           count={linePoints.length}
//           array={new Float32Array(linePoints.flatMap((p) => [p.x, p.y, p.z]))}
//           itemSize={3}
//         />
//       </bufferGeometry>
//       <lineBasicMaterial color={0xff0000} />
//     </line>
//   );
// };

// const Scene: React.FC<{ meshes?: MeshData[]; lines?: LineData }> = ({
//   meshes = [],
//   lines,
// }) => {
//   const { camera } = useThree();

//   useEffect(() => {
//     camera.position.set(100, 0, 0);
//   }, [camera]);

//   return (
//     <>
//       <ambientLight intensity={0.4} color={0x404040} />
//       <hemisphereLight
//         intensity={1}
//         color={0xffffbb}
//         groundColor={0x080820}
//       />

//       {meshes.map((meshData, index) => (
//         <Mesh3D
//           key={`mesh-${index}`}
//           vertices={meshData.vertices}
//           triangles={meshData.triangles}
//           metadata={meshData.metadata}
//         />
//       ))}

//       {lines?.lines.map((line, index) => (
//         <Line3D key={`line-${index}`} line={line} />
//       ))}

//       <OrbitControls />
//     </>
//   );
// };

// const Viewer3D: React.FC<Viewer3DProps> = ({
//   width = 500,
//   height = 500,
//   meshes = [],
//   lines,
//   backgroundColor = 0x363432,
// }) => {
//   return (
//     <Canvas
//       style={{ width, height }}
//       camera={{ fov: 75, near: 0.1, far: 2000 }}
//       gl={{ antialias: true }}
//     >
//       <color attach="background" args={[backgroundColor]} />
//       <Scene meshes={meshes} lines={lines} />
//     </Canvas>
//   );
// };

// export default Viewer3D;
// export type { MeshData, LineData, Viewer3DProps };

import { useRef, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import * as THREE from 'three'

interface BoxProps {
  position: [number, number, number]
}

function Box(props: BoxProps) {
  // This reference gives us direct access to the THREE.Mesh object
  const ref = useRef<THREE.Mesh>(null)
  // Hold state for hovered and clicked events
  const [hovered, hover] = useState<boolean>(false)
  const [clicked, click] = useState<boolean>(false)
  // Subscribe this component to the render-loop, rotate the mesh every frame
  useFrame((state, delta) => {
    if (ref.current) {
      ref.current.rotation.x += delta
    }
  })
  // Return the view, these are regular Threejs elements expressed in JSX
  return (
    <mesh
      {...props}
      ref={ref}
      scale={clicked ? 1.5 : 1}
      onClick={(event: any) => click(!clicked)}
      onPointerOver={(event: any) => (event.stopPropagation(), hover(true))}
      onPointerOut={(event: any) => hover(false)}>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color={hovered ? 'hotpink' : 'orange'} />
    </mesh>
  )
}

export default function Viewer3D() {
  return (
    <Canvas>
      <ambientLight intensity={Math.PI / 2} />
      <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} decay={0} intensity={Math.PI} />
      <pointLight position={[-10, -10, -10]} decay={0} intensity={Math.PI} />
      <Box position={[-1.2, 0, 0]} />
      <Box position={[1.2, 0, 0]} />
      <OrbitControls />
    </Canvas>
  )
}
