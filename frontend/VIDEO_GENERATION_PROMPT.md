# AI Video Generation Prompt for Agent Constellation

## Video Specifications
- **Duration**: 10-15 seconds (loopable)
- **Resolution**: 1920x1080 (Full HD) or 3840x2160 (4K)
- **Format**: MP4 (H.264 codec)
- **Frame Rate**: 60 FPS for smooth motion
- **Style**: Professional, modern, governmental, clean

---

## Main Prompt for AI Video Generation

```
Create a professional, modern 3D animated video showing a smart city governance coordination system. 

SCENE SETUP:
- Clean, professional background with subtle gradient from light blue-gray (#f1f5f9) to off-white (#f8fafc)
- Soft ambient lighting with a gentle blue glow (#3b82f6) emanating from the center
- Depth of field effect with slight blur on distant elements

CENTER COORDINATION HUB:
- A glowing, pulsating brain icon or neural network node at the center
- Main color: Professional blue (#3b82f6) with golden accents (#d4af37)
- Subtle rotation (360° over 20 seconds)
- Gentle pulsing glow effect (expanding and contracting smoothly)
- Emits soft light particles that drift outward
- Size: Medium-large, visually dominant

SIX ORBITING DEPARTMENT AGENTS (arrange in 3D elliptical orbit around center):

1. WATER DEPARTMENT (Blue #60a5fa):
   - Icon: Water droplet or wave symbol
   - Orbital position: Front-right of ellipse
   - Size: Medium sphere with icon inside
   - Glow: Soft blue aura

2. FIRE DEPARTMENT (Orange #fb923c):
   - Icon: Flame symbol
   - Orbital position: Upper-center of ellipse
   - Size: Medium sphere with icon inside
   - Glow: Warm orange aura

3. ENGINEERING DEPARTMENT (Teal #2dd4bf):
   - Icon: Wrench or gear symbol
   - Orbital position: Front-left of ellipse
   - Size: Medium sphere with icon inside
   - Glow: Teal-cyan aura

4. HEALTH DEPARTMENT (Pink #f472b6):
   - Icon: Heart or medical cross symbol
   - Orbital position: Back-right of ellipse
   - Size: Medium sphere with icon inside
   - Glow: Soft pink aura

5. FINANCE DEPARTMENT (Gold #fbbf24):
   - Icon: Dollar sign or coin symbol
   - Orbital position: Back-left of ellipse
   - Size: Medium sphere with icon inside
   - Glow: Golden aura

6. SANITATION DEPARTMENT (Purple #a78bfa):
   - Icon: Recycling or trash bin symbol
   - Orbital position: Lower-center of ellipse
   - Size: Medium sphere with icon inside
   - Glow: Purple-lavender aura

ANIMATION MOVEMENTS:
- All 6 agents orbit around the center in a smooth 3D elliptical path
- Orbital rotation: Complete 360° orbit in 15 seconds (slow, elegant)
- Each sphere rotates gently on its own axis
- As agents move to the front of the ellipse, they scale up slightly (1.1x)
- As agents move to the back of the ellipse, they scale down slightly (0.7x)
- Depth: Front agents appear larger and brighter, back agents smaller and slightly faded

CONNECTING ELEMENTS:
- Thin, glowing lines connecting each agent to the central hub
- Lines pulse with energy traveling from agents to center and back
- Line color: Semi-transparent white (#ffffff) at 30% opacity
- Energy pulse particles (small dots) travel along the lines
- Occasional spark/flash at connection points

PARTICLE EFFECTS:
- 30-50 small floating particles throughout the space
- Colors: Mix of blue (#3b82f6), teal (#14b8a6), gold (#d4af37), purple (#8b5cf6)
- Particles drift slowly in random directions
- Subtle bloom/glow effect on all particles
- Some particles cluster near the orbital paths

DEPTH & PERSPECTIVE:
- Camera angle: Slightly elevated (15° above horizontal)
- Subtle camera movement: Very slow zoom in (1.0x to 1.05x over duration)
- 3D perspective with proper depth rendering
- Orbital path tilted at 30° angle for dynamic 3D effect

LIGHTING:
- Main light source from center (blue-white)
- Rim lighting on spheres for definition
- Soft shadows beneath agents (very subtle)
- Ambient occlusion for depth
- No harsh shadows - keep it professional and clean

MOOD & STYLE:
- Professional and governmental
- High-tech but approachable
- Clean and organized (not chaotic)
- Smooth, fluid motion (no jittery movements)
- Premium quality, polished look
- Inspiring confidence and coordination
```

---

## Alternative Shorter Prompt (for quick generation)

```
3D animation: Professional city governance visualization. Central glowing blue brain hub (#3b82f6) with 6 colored spheres orbiting in smooth 3D ellipse. Spheres: blue water droplet, orange flame, teal wrench, pink heart, gold dollar sign, purple recycling bin. Each sphere glows with its color, connected to center by pulsing light lines. Clean gradient background (light blue-gray to off-white). Floating particles, depth of field. Smooth rotation, professional government aesthetic, 60fps, loopable. Camera slowly zooms in. Premium quality.
```

---

## Technical Parameters for AI Tools

### For Runway ML Gen-3:
```
Style: 3D render, professional animation, clean aesthetic
Motion: Slow orbital rotation, smooth camera movement
Quality: Maximum
Duration: 10 seconds
Aspect Ratio: 16:9
```

### For Pika Labs:
```
Parameters: -motion 2 -fps 24 -camera slow zoom -style professional 3d render -quality high
```

### For Stable Video Diffusion:
```
Seed: (random for variation)
Motion bucket: 127 (medium motion)
Frames: 300 (for 10s at 30fps)
Decode chunk size: 8
```

---

## Post-Production Tips

1. **Loop Preparation**: 
   - Trim to exact loop point where animation repeats
   - Add 0.5s crossfade at loop point for seamless transition

2. **Optimization**:
   - Compress to reasonable file size (target: 2-5MB for web)
   - Use H.264 codec with high profile
   - Bitrate: 5-8 Mbps for 1080p

3. **Fallback Options**:
   - Export as WebM for better browser support
   - Create animated GIF version (lower quality) as fallback
   - Prepare static poster frame for loading state

4. **Enhancement** (if needed):
   - Add subtle motion blur in After Effects
   - Color grade for consistency
   - Add slight vignette for focus
   - Enhance glow effects if AI output is too flat

---

## Integration in Code

Replace the constellation component with video element:

```jsx
<video 
  autoPlay 
  loop 
  muted 
  playsInline
  className="w-full h-full object-cover rounded-2xl"
  poster="/agent-constellation-poster.jpg"
>
  <source src="/videos/agent-constellation.mp4" type="video/mp4" />
  <source src="/videos/agent-constellation.webm" type="video/webm" />
  {/* Fallback for browsers that don't support video */}
  <img src="/agent-constellation-poster.jpg" alt="Agent Constellation" />
</video>
```

---

## Additional Variations to Try

### Variation 1: Data Flow Emphasis
Add data stream visualization - binary numbers and code snippets flowing along the connecting lines from agents to center hub.

### Variation 2: City Blueprint Background
Subtle translucent city infrastructure blueprints visible in the background, slowly rotating opposite to the main orbit.

### Variation 3: Pulse Synchronization
All agents pulse in synchronized rhythm, creating a "heartbeat" effect for the entire system every 3 seconds.

### Variation 4: Interactive Highlight
One agent at a time briefly glows brighter and scales up (1.3x) for 1.5 seconds, cycling through all 6 agents.

---

## Color Reference Guide

| Department | Primary Color | Hex Code | Accent Color | Hex Code |
|-----------|--------------|----------|--------------|----------|
| Coordination Hub | Gov Blue | #3b82f6 | Light Blue | #60a5fa |
| Water | Sky Blue | #60a5fa | Lighter Blue | #93c5fd |
| Fire | Orange | #fb923c | Light Orange | #fdba74 |
| Engineering | Teal | #2dd4bf | Aqua | #5eead4 |
| Health | Pink | #f472b6 | Light Pink | #f9a8d4 |
| Finance | Gold | #fbbf24 | Light Gold | #fcd34d |
| Sanitation | Purple | #a78bfa | Lavender | #c4b5fd |
| Background | Light Gray | #f1f5f9 | Off White | #f8fafc |
| Accent Gold | Gold | #d4af37 | Light Gold | #f0d98f |

---

## File Naming Convention

- Primary: `agent-constellation-loop.mp4`
- WebM version: `agent-constellation-loop.webm`
- Poster frame: `agent-constellation-poster.jpg`
- Optimized mobile: `agent-constellation-mobile.mp4`

---

## Recommended AI Tools

1. **Runway ML Gen-3** (Best for complex 3D animations)
   - Pros: High quality, good motion control
   - Cons: Expensive, may require multiple iterations

2. **Pika Labs 1.0** (Great for stylized motion)
   - Pros: Good at smooth movements, affordable
   - Cons: Less control over exact positioning

3. **Leonardo.ai Motion** (Good for creative effects)
   - Pros: Fast, cost-effective
   - Cons: Less precise for orbital mechanics

4. **Genmo** (Free alternative)
   - Pros: Free tier available
   - Cons: Lower quality output

5. **Custom After Effects** (Full control)
   - Pros: Complete control, professional
   - Cons: Time-intensive, requires skills

---

## Success Metrics

✅ Smooth 60fps playback without stuttering
✅ Perfect loop with no visible seam
✅ File size under 5MB for fast web loading
✅ Recognizable department icons/symbols
✅ Professional governmental aesthetic
✅ All 6 agents clearly visible and distinguishable
✅ Central coordination hub visually dominant
✅ Engaging but not distracting motion
