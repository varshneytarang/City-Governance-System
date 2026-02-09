# 🎬 Quick Copy-Paste Prompts for AI Video Tools

Choose your AI tool and copy the corresponding prompt below.

---

## 🚀 Runway ML Gen-3 (Recommended - Best Quality)

**Copy this prompt:**

```
Professional 3D animation for city governance coordination system. Central glowing neural hub (blue #3b82f6) with gentle pulse and rotation. Six department spheres orbit in smooth 3D ellipse around center: 1) Blue water droplet (#60a5fa) front-right, 2) Orange flame (#fb923c) top, 3) Teal wrench (#2dd4bf) front-left, 4) Pink heart (#f472b6) back-right, 5) Gold dollar sign (#fbbf24) back-left, 6) Purple recycling bin (#a78bfa) bottom. Each sphere has soft glow matching its color. Thin white energy lines connect all spheres to center with pulsing particles traveling along them. Clean gradient background from light blue-gray to off-white. 30-50 floating particles with bloom effects. Orbital rotation completes in 15 seconds. Professional governmental aesthetic, smooth motion, 60fps, must loop seamlessly. Camera slowly zooms from 1.0x to 1.05x. High quality 3D render with proper depth, shadows, and lighting.

Settings: Motion 8/10, Camera Motion: Slow Zoom, Quality: Maximum, 10 seconds
```

---

## 🎨 Pika Labs

**Copy this prompt:**

```
3D rendered city governance visualization. Glowing blue brain hub (#3b82f6) at center with gentle pulse. Six colored spheres orbit smoothly in 3D ellipse: blue water (#60a5fa), orange fire (#fb923c), teal engineering (#2dd4bf), pink health (#f472b6), gold finance (#fbbf24), purple sanitation (#a78bfa). Each sphere glows and connects to center with pulsing energy lines. Floating particles throughout. Professional, clean aesthetic. Light blue-gray gradient background. Smooth orbital rotation, 15-second loop. Camera slowly zooms in. High quality, polished, governmental style.

--motion 3 --fps 60 --camera slow-zoom --style professional-3d --quality high --ar 16:9
```

---

## ⚡ Leonardo.ai Motion

**Copy this prompt:**

```
Professional 3D animation showing smart city coordination. Central blue glowing neural hub surrounded by 6 department spheres orbiting in ellipse: water (blue), fire (orange), engineering (teal), health (pink), finance (gold), sanitation (purple). Energy lines connect spheres to center. Clean professional background. Smooth rotation, particles floating, governmental aesthetic.

Motion Strength: 7/10
Style: 3D Render
Quality: High
Dimension: 16:9
```

---

## 🎯 Genmo (Free Option)

**Copy this prompt:**

```
3D city governance system: central glowing blue hub with 6 colored orbiting spheres (blue, orange, teal, pink, gold, purple) connected by energy lines. Professional, clean, smooth rotation, particles, governmental style.

Motion: Medium
Duration: 6 seconds (will need to loop)
```

---

## 🎬 Stable Video Diffusion

**Image-to-Video Approach:**

First, generate a still image with this prompt:
```
Professional 3D render of smart city coordination system, central glowing blue neural network hub with six colored department spheres arranged in circular orbit, energy lines connecting to center, floating particles, clean light blue gradient background, governmental aesthetic, high quality render, 8k
```

Then use SVD with:
```
Motion Bucket: 127 (medium motion)
Frames: 125 (for 4s at 30fps - will need to loop)
Seed: [random]
FPS: 30
```

---

## 🎨 Midjourney → Runway Pipeline

### Step 1: Generate Image in Midjourney

```
professional 3D render of city governance coordination system, central glowing neural brain in blue (#3b82f6), six department spheres orbiting in perfect ellipse: water droplet blue, fire flame orange, engineering wrench teal, health heart pink, finance dollar gold, sanitation recycling purple, energy lines connecting all to center, floating particles, clean gradient background light blue to white, governmental professional aesthetic, ultra high quality, 8k, dramatic lighting, depth of field --ar 16:9 --style raw --v 6
```

### Step 2: Animate in Runway
Use the generated image with Gen-3 image-to-video:
```
Smooth orbital rotation of spheres, gentle hub pulse, floating particles, slow camera zoom, 10 seconds
```

---

## 📝 Alternative Short Prompt (Universal)

For any tool that has character limits:

```
3D smart city coordination: blue glowing center hub, 6 colored orbiting spheres (water, fire, engineering, health, finance, sanitation), energy connections, professional governmental style, smooth loop
```

---

## 🎯 After Effects Composition Guide

If creating manually:

1. **Canvas**: 1920x1080, 10 seconds, 60fps
2. **Center Hub**: 
   - Blue (#3b82f6) sphere, 200px diameter
   - Add glow (50px), rotation (1 rev/20s), pulse scale (100-110%)
3. **Agent Spheres**: 
   - 6 spheres, 80px each
   - Positions on ellipse: radiusX=450px, radiusY=200px
   - Rotation: 1 rev/15s clockwise
   - Z-space: -100 to +100 for depth
4. **Connections**: 
   - Beam effect from CC Light Rays
   - Opacity 30%, white color
   - Particle emitters on paths
5. **Background**: 
   - Gradient ramp: #f1f5f9 to #f8fafc
   - Add camera layer for zoom
6. **Particles**: 
   - CC Particle Systems II
   - 40-50 particles, various colors
   - Slow drift, bloom glow

---

## ✅ Quality Checklist

Before finalizing, verify your video has:

- [ ] Smooth 60fps (or 30fps minimum)
- [ ] Perfect loop (no visible seam)
- [ ] All 6 agent colors correct and distinct
- [ ] Central hub is visually dominant
- [ ] Energy connections visible
- [ ] Clean professional aesthetic
- [ ] Proper depth (3D effect)
- [ ] File size under 10MB (before optimization)
- [ ] Duration 10-15 seconds
- [ ] 1920x1080 resolution minimum

---

## 🎬 Tool Comparison

| Tool | Quality | Speed | Cost | Best For |
|------|---------|-------|------|----------|
| Runway Gen-3 | ⭐⭐⭐⭐⭐ | Medium | $$ | Best overall |
| Pika Labs | ⭐⭐⭐⭐ | Fast | $ | Quick iterations |
| Leonardo Motion | ⭐⭐⭐ | Fast | $ | Budget option |
| Midjourney+Runway | ⭐⭐⭐⭐⭐ | Slow | $$$ | Maximum quality |
| Genmo | ⭐⭐ | Fast | Free | Testing/proof |
| After Effects | ⭐⭐⭐⭐⭐ | Very Slow | Free | Full control |

---

## 💡 Pro Tips

1. **Generate multiple variations** and pick the best
2. **Add "seamless loop" to prompt** for better results
3. **Export at highest quality** - you'll compress later
4. **Test the loop** before optimization
5. **Keep source file** in case you need to re-export

---

## 🚨 Common Issues & Fixes

**Issue**: AI generates incorrect number of spheres
→ Be very explicit: "exactly six spheres, no more, no less"

**Issue**: Colors don't match
→ Include hex codes in prompt and reference image

**Issue**: Motion too fast/slow
→ Specify duration: "smooth rotation completing in exactly 15 seconds"

**Issue**: Doesn't loop well
→ Add "perfect seamless loop" and check "loop" in tool settings

---

## 📤 After Generation

Once you have your video:

1. Download at highest quality available
2. Run the optimization script:
   ```powershell
   .\optimize-video.ps1 -InputVideo "your-video.mp4"
   ```
3. Place files in `frontend/public/videos/`
4. Test in browser
5. Deploy!

---

**Ready to generate?** Pick a tool above, copy the prompt, and create your video!
