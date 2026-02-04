import React, { useRef, useMemo, useState } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { OrbitControls, Sky } from '@react-three/drei'
import { EffectComposer, Bloom } from '@react-three/postprocessing'
import * as THREE from 'three'

import agents from '../data/agents'

function CentralHub() {
  const ref = useRef()
  useFrame((state, delta) => {
    if (ref.current) ref.current.rotation.y += delta * 0.25
  })
  return (
    <mesh ref={ref} position={[0, -8, 0]}>
      <icosahedronGeometry args={[28, 2]} />
      <meshStandardMaterial color={'#d4af37'} roughness={0.2} metalness={0.8} emissive={'#d4af37'} emissiveIntensity={0.12} />
    </mesh>
  )
}

function Agents3D() {
  const { gl, camera } = useThree()
  const groupRef = useRef()
  const lineRefs = useRef([])
  const meshRefs = useRef([])
  const draggingRef = useRef(null)

  // initialize positions in a circle
  const positions = useMemo(() => {
    return agents.map((a, i) => {
      const angle = (i / agents.length) * Math.PI * 2
      const r = 160
      return new THREE.Vector3(Math.cos(angle) * r, (i % 2 === 0 ? -6 : 6), Math.sin(angle) * r)
    })
  }, [])

  // pointer handlers (set on each mesh)
  const handlePointerDown = (e, idx) => {
    e.stopPropagation()
    draggingRef.current = { idx, pointerId: e.pointerId }
    e.target.setPointerCapture(e.pointerId)
    document.body.style.cursor = 'grabbing'
  }

  const handlePointerUp = (e, idx) => {
    e.stopPropagation()
    if (draggingRef.current && draggingRef.current.pointerId === e.pointerId) {
      draggingRef.current = null
      try { e.target.releasePointerCapture(e.pointerId) } catch (err) {}
      document.body.style.cursor = 'auto'
    }
  }

  const handlePointerMove = (e, idx) => {
    if (!draggingRef.current || draggingRef.current.idx !== idx) return
    e.stopPropagation()
    // project pointer ray onto ground plane y = positions[idx].y
    const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), -positions[idx].y)
    const intersection = new THREE.Vector3()
    e.ray.intersectPlane(plane, intersection)
    if (intersection) {
      positions[idx].copy(intersection)
      // update mesh position
      const m = meshRefs.current[idx]
      if (m) m.position.copy(positions[idx])
    }
  }

  useFrame(() => {
    // update lines connecting to center and project positions to DOM
    const size = { width: gl.domElement.clientWidth, height: gl.domElement.clientHeight }
    positions.forEach((pos, i) => {
      const line = lineRefs.current[i]
      if (line) {
        const pts = [new THREE.Vector3(0, -8, 0), pos]
        line.geometry.setFromPoints(pts)
      }

      // project to screen and update DOM overlay
      const proj = pos.clone().project(camera)
      const x = (proj.x + 1) / 2 * size.width
      const y = (1 - (proj.y + 1) / 2) * size.height
      const dom = document.getElementById(`agent-dom-${agents[i].id}`)
      if (dom) {
        // position relative to the parent container (AgentConstellation section)
        dom.style.position = 'absolute'
        dom.style.transform = `translate(-50%, -50%) translate(${x}px, ${y}px)`
        dom.style.pointerEvents = 'auto'
      }
    })
  })

  return (
    <group ref={groupRef}>
      {agents.map((a, i) => (
        <group key={a.id}>
          <mesh
            ref={el => (meshRefs.current[i] = el)}
            position={positions[i].toArray()}
            onPointerDown={(e) => handlePointerDown(e, i)}
            onPointerUp={(e) => handlePointerUp(e, i)}
            onPointerMove={(e) => handlePointerMove(e, i)}
            castShadow
          >
            <sphereGeometry args={[10, 32, 32]} />
            <meshStandardMaterial color={a.color} emissive={a.color} emissiveIntensity={0.15} metalness={0.6} roughness={0.3} />
          </mesh>

          <line ref={el => (lineRefs.current[i] = el)}>
            <bufferGeometry />
            <lineBasicMaterial color={a.color} transparent opacity={0.28} linewidth={2} />
          </line>
        </group>
      ))}
    </group>
  )
}

const AgentScene = ({ reducedMotion }) => {
  if (reducedMotion) return null

  return (
    <div className="absolute inset-0 w-full h-full z-0 pointer-events-none">
      <Canvas camera={{ position: [0, 40, 420], fov: 45 }} linear gl={{ antialias: true }}>
        <ambientLight intensity={0.6} />
        <directionalLight position={[60, 120, 60]} intensity={0.9} />

        <Sky sunPosition={[100, 20, 100]} distance={450} turbidity={6} rayleigh={0.4} />

        <group>
          <CentralHub />
          <Agents3D />
        </group>

        <EffectComposer disableNormalPass>
          <Bloom luminanceThreshold={0.2} mipmapBlur luminanceSmoothing={0.6} intensity={0.8} />
        </EffectComposer>

        <OrbitControls enableZoom={false} enablePan={false} autoRotate={false} />
      </Canvas>
    </div>
  )
}

export default AgentScene
