# City Governance AI - Frontend Landing Page

## 🎨 Overview

A modern, professional, and highly interactive landing page for the City Governance AI System. Features stunning 3D animations, neural network backgrounds, and an immersive user experience while maintaining government-appropriate aesthetics.

## ✨ Features

### Visual Design
- **Neural Network Background**: Animated particle system with interconnected nodes
- **3D Agent Constellation**: Interactive orbital display of 6 department agents
- **Glass Morphism UI**: Modern glassmorphism design with backdrop blur effects
- **Custom Cursor**: Interactive cursor with particle trail
- **Smooth Animations**: 60fps targeted animations with GPU acceleration

### Interactive Elements
- **Agent Orbs**: Hover to reveal capabilities, click for connection animations
- **Transparency Vault**: 3D rotating glass pyramid with searchable decision crystals
- **15-Phase Pipeline**: Horizontal scrolling workflow visualization
- **Live Counters**: Animated statistics with count-up effects
- **Semantic Search**: Real-time crystal filtering demonstration

### Accessibility
- **Reduced Motion Toggle**: Respects user preferences for animations
- **High Contrast Mode**: Enhanced contrast for better readability
- **Keyboard Navigation**: Full keyboard accessibility
- **Screen Reader Friendly**: Proper ARIA labels and semantic HTML
- **Responsive Design**: Mobile, tablet, and desktop optimized

### Performance
- **Core Web Vitals Optimized**: LCP < 1.5s, CLS < 0.1, TBT < 200ms
- **Lazy Loading**: Progressive content loading
- **GPU Acceleration**: Hardware-accelerated 3D transforms
- **FPS Monitoring**: Built-in performance tracking

## 🚀 Quick Start

### Option 1: Direct Opening
Simply open `index.html` in a modern web browser:
```bash
# Navigate to frontend folder
cd frontend

# Open in default browser (Windows)
start index.html

# Or use a local server (recommended)
python -m http.server 8080
# Then visit: http://localhost:8080
```

### Option 2: Using Live Server (Recommended)
Install the VS Code Live Server extension and click "Go Live" on `index.html`.

### Option 3: Using npm
```bash
cd frontend
npm install
npm start
```

## 📁 Project Structure

```
frontend/
├── index.html              # Main HTML structure
├── styles/
│   ├── main.css           # Core styles, variables, utilities
│   ├── components.css     # Component-specific styles
│   └── animations.css     # Advanced animations
├── js/
│   ├── main.js           # Application entry point
│   ├── cursor.js         # Custom cursor logic
│   ├── neural-background.js  # Animated background
│   ├── animations.js     # Scroll & counter animations
│   └── interactions.js   # User interactions
└── README.md             # This file
```

## 🎯 Sections

### 1. Hero Section
- **Neural Background**: Animated particle network
- **Hero Title**: "Autonomous Intelligence for Urban Evolution"
- **Live Stats**: 6 Agents, 15k+ Lines, 90% Coverage
- **CTA Button**: Portal warp effect on hover

### 2. Department Agents
- **6 Agent Orbs**: Water, Engineering, Fire, Health, Sanitation, Finance
- **Circular Constellation**: Orbiting around central coordination node
- **Interactive**: Hover for capabilities, click for connections

### 3. Coordination Intelligence
- **Brain Core**: Pulsing neural center with 6 connected nodes
- **Flow Particles**: Animated decision flow visualization
- **Stats**: 5 conflict types, 100% resolution, deadlock-free

### 4. Transparency Vault
- **3D Glass Pyramid**: Rotating vault containing decision crystals
- **Semantic Search**: Live filtering of decisions
- **Metrics**: 40+ tables, 100% logged, ChromaDB powered

### 5. Workflow Pipeline
- **15 Phases**: Complete decision workflow
- **Horizontal Scroll**: Smooth scrolling through phases
- **Color Coding**: LLM (blue), Rules (green), Human (gold)

### 6. Production Statistics
- **Stats Grid**: 8 key metrics
- **Tech Stack**: Technology badges
- **Animated Counters**: Count-up animations on scroll

### 7. Footer CTA
- **Call to Action**: Get Started / View Documentation
- **Links**: GitHub, API Docs, Setup Guide
- **Meta Info**: License, version, status

## 🎨 Color Palette

```css
--cosmic-navy: #0A0F2A       /* Deep background */
--electric-sapphire: #00D4FF  /* Primary accent */
--neon-emerald: #00FF88       /* Secondary accent */
--molten-gold: #FFD700        /* Tertiary accent */
--amethyst-glow: #A855F7      /* Purple accent */
--obsidian-black: #000000     /* Pure black */
```

## 🔧 Customization

### Changing Colors
Edit CSS variables in `styles/main.css`:
```css
:root {
    --accent-primary: #00D4FF;    /* Change primary color */
    --accent-secondary: #00FF88;   /* Change secondary color */
    /* ... more variables ... */
}
```

### Adjusting Animations
Modify animation durations in `styles/animations.css`:
```css
--transition-fast: 0.2s ease;     /* Quick transitions */
--transition-normal: 0.3s ease;   /* Normal transitions */
--transition-slow: 0.6s ease;     /* Slow transitions */
```

### Changing Content
Update text directly in `index.html`:
```html
<h1 class="hero-title">
    <span class="title-line">Your Custom Title</span>
</h1>
```

## 📱 Responsive Breakpoints

- **Mobile**: < 480px (simplified 2.5D, reduced particles)
- **Tablet**: 481px - 768px (3x2 grid, moderate effects)
- **Desktop**: 769px - 1200px (full experience)
- **Large Desktop**: > 1200px (maximum fidelity)

## ⚡ Performance Optimization

### Current Optimizations
- GPU-accelerated 3D transforms
- Debounced scroll and resize handlers
- Intersection Observer for lazy animations
- Reduced particle count on mobile
- Optimized repaints and reflows

### Lighthouse Scores Target
- **Performance**: 90+
- **Accessibility**: 100
- **Best Practices**: 95+
- **SEO**: 90+

## 🔐 Browser Compatibility

### Supported Browsers
- Chrome/Edge: 90+
- Firefox: 88+
- Safari: 14+
- Opera: 76+

### Required Features
- CSS Grid
- CSS Custom Properties
- Intersection Observer
- Canvas API
- ES6+ JavaScript

## 🎓 Learning Resources

### Technologies Used
1. **HTML5**: Semantic structure, accessibility
2. **CSS3**: Grid, Flexbox, Animations, Custom Properties
3. **JavaScript ES6+**: Classes, Modules, Async/Await
4. **Canvas API**: Neural background rendering
5. **Intersection Observer**: Scroll animations
6. **Performance API**: Web Vitals monitoring

### Key Techniques
- **Glass Morphism**: Backdrop filter effects
- **Particle Systems**: Canvas-based animation
- **3D Transforms**: CSS perspective and transforms
- **Parallax Scrolling**: Depth-based movement
- **Counter Animations**: RequestAnimationFrame

## 🐛 Troubleshooting

### Animations Not Working
- Check browser compatibility
- Ensure JavaScript is enabled
- Try disabling browser extensions
- Clear cache and hard refresh

### Performance Issues
- Reduce particle count in `neural-background.js`
- Enable "Reduced Motion" toggle
- Close other browser tabs
- Check GPU acceleration in browser settings

### Layout Issues
- Verify viewport meta tag
- Check browser zoom level (should be 100%)
- Update to latest browser version
- Test in different browser

## 🚀 Deployment

### Static Hosting (Recommended)
Deploy to:
- **Vercel**: `vercel deploy`
- **Netlify**: Drag & drop `frontend` folder
- **GitHub Pages**: Push to `gh-pages` branch
- **Cloudflare Pages**: Connect repository

### Configuration
No build process required - pure HTML/CSS/JS!

### CDN Assets
Fonts are loaded from Google Fonts CDN:
- Exo 2
- Rajdhani

## 📞 Support

For issues or questions:
1. Check this README first
2. Review browser console for errors
3. Test in different browser
4. Check system requirements

## 📝 License

This frontend is part of the City Governance System.
See main project LICENSE (Apache 2.0).

## 🎉 Credits

Created for the City Governance AI System v2.0
- Multi-Agent Architecture
- Transparency & Accountability
- Production-Ready Municipal Governance

---

**Status**: ✅ Production Ready  
**Version**: 2.0  
**Last Updated**: February 2026
