import React, { useEffect, useState } from 'react'

const CustomCursor = () => {
  const [position, setPosition] = useState({ x: 0, y: 0 })
  const [isPointer, setIsPointer] = useState(false)
  const [trail, setTrail] = useState([])

  useEffect(() => {
    const handleMouseMove = (e) => {
      setPosition({ x: e.clientX, y: e.clientY })
      
      // Update trail
      setTrail(prev => [
        ...prev.slice(-8),
        { x: e.clientX, y: e.clientY, id: Date.now() }
      ])
    }

    const handleMouseOver = (e) => {
      if (e.target.tagName === 'BUTTON' || 
          e.target.tagName === 'A' ||
          e.target.closest('button') ||
          e.target.closest('a')) {
        setIsPointer(true)
      } else {
        setIsPointer(false)
      }
    }

    window.addEventListener('mousemove', handleMouseMove)
    window.addEventListener('mouseover', handleMouseOver)

    return () => {
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('mouseover', handleMouseOver)
    }
  }, [])

  // Hide on mobile
  if (window.innerWidth < 768) return null

  return (
    <>
      {/* Trail particles */}
      {trail.map((point, index) => (
        <div
          key={point.id}
          className="fixed w-1.5 h-1.5 rounded-full bg-accent-gold pointer-events-none z-50"
          style={{
            left: point.x,
            top: point.y,
            opacity: (index + 1) / trail.length * 0.4,
            transform: 'translate(-50%, -50%)',
            transition: 'opacity 0.3s ease-out'
          }}
        />
      ))}

      {/* Main cursor */}
      <div
        className={`fixed w-7 h-7 rounded-full border-2 border-gov-blue pointer-events-none z-50 transition-transform duration-150 ${
          isPointer ? 'scale-150 bg-accent-gold/20 border-accent-gold' : 'scale-100'
        }`}
        style={{
          left: position.x,
          top: position.y,
          transform: `translate(-50%, -50%) ${isPointer ? 'scale(1.5)' : 'scale(1)'}`,
          boxShadow: isPointer ? '0 0 20px rgba(212, 175, 55, 0.4)' : '0 0 12px rgba(59, 130, 246, 0.3)'
        }}
      />
    </>
  )
}

export default CustomCursor
