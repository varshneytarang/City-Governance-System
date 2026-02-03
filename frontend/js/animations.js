// Main Animations and Scroll Effects
class ScrollAnimations {
    constructor() {
        this.sections = document.querySelectorAll('section');
        this.options = {
            threshold: 0.2,
            rootMargin: '0px 0px -100px 0px'
        };
        
        this.init();
    }
    
    init() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    this.animateSection(entry.target);
                }
            });
        }, this.options);
        
        this.sections.forEach(section => {
            observer.observe(section);
        });
    }
    
    animateSection(section) {
        // Stagger animation for child elements
        const children = section.querySelectorAll('.stat-card, .agent-orb, .coord-stat, .pipeline-node');
        
        children.forEach((child, index) => {
            setTimeout(() => {
                child.style.opacity = '1';
                child.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }
}

// Counter Animation
class CounterAnimation {
    constructor() {
        this.counters = document.querySelectorAll('.stat-number[data-count]');
        this.animated = new Set();
        this.init();
    }
    
    init() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !this.animated.has(entry.target)) {
                    this.animateCounter(entry.target);
                    this.animated.add(entry.target);
                }
            });
        }, { threshold: 0.5 });
        
        this.counters.forEach(counter => observer.observe(counter));
    }
    
    animateCounter(element) {
        const target = parseInt(element.getAttribute('data-count'));
        const duration = 2000;
        const increment = target / (duration / 16);
        let current = 0;
        
        const updateCounter = () => {
            current += increment;
            if (current < target) {
                element.textContent = Math.floor(current).toLocaleString();
                requestAnimationFrame(updateCounter);
            } else {
                element.textContent = target.toLocaleString();
            }
        };
        
        updateCounter();
    }
}

// Parallax Effect
class ParallaxEffect {
    constructor() {
        this.elements = document.querySelectorAll('[data-parallax]');
        this.init();
    }
    
    init() {
        window.addEventListener('scroll', () => {
            this.elements.forEach(element => {
                const speed = element.getAttribute('data-parallax') || 0.5;
                const yPos = -(window.pageYOffset * speed);
                element.style.transform = `translateY(${yPos}px)`;
            });
        });
    }
}

// Glitch Effect on Hover
class GlitchEffect {
    constructor() {
        this.glitchElements = document.querySelectorAll('.title-line');
        this.init();
    }
    
    init() {
        this.glitchElements.forEach(element => {
            element.addEventListener('mouseenter', () => {
                this.applyGlitch(element);
            });
        });
    }
    
    applyGlitch(element) {
        const originalText = element.textContent;
        const glitchChars = '!@#$%^&*()_+-=[]{}|;:,.<>?';
        let iterations = 0;
        
        const interval = setInterval(() => {
            element.textContent = originalText
                .split('')
                .map((char, index) => {
                    if (index < iterations) {
                        return originalText[index];
                    }
                    return glitchChars[Math.floor(Math.random() * glitchChars.length)];
                })
                .join('');
            
            iterations += 1/3;
            
            if (iterations >= originalText.length) {
                clearInterval(interval);
                element.textContent = originalText;
            }
        }, 30);
    }
}

// Particle System for Hero
class ParticleSystem {
    constructor() {
        this.container = document.querySelector('.particle-container');
        if (!this.container) return;
        
        this.createParticles();
    }
    
    createParticles() {
        const particleCount = window.innerWidth < 768 ? 20 : 50;
        
        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            
            const size = Math.random() * 4 + 2;
            const x = Math.random() * 100;
            const y = Math.random() * 100;
            const duration = Math.random() * 20 + 10;
            const delay = Math.random() * 5;
            
            particle.style.cssText = `
                position: absolute;
                width: ${size}px;
                height: ${size}px;
                background: var(--accent-primary);
                border-radius: 50%;
                left: ${x}%;
                top: ${y}%;
                opacity: ${Math.random() * 0.5 + 0.2};
                box-shadow: 0 0 ${size * 2}px var(--accent-primary);
                animation: float ${duration}s ease-in-out ${delay}s infinite;
            `;
            
            this.container.appendChild(particle);
        }
    }
}

// Initialize all animations
document.addEventListener('DOMContentLoaded', () => {
    new ScrollAnimations();
    new CounterAnimation();
    new ParallaxEffect();
    new GlitchEffect();
    new ParticleSystem();
    
    // Add float animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes float {
            0%, 100% {
                transform: translateY(0) translateX(0);
            }
            25% {
                transform: translateY(-20px) translateX(10px);
            }
            50% {
                transform: translateY(-10px) translateX(-10px);
            }
            75% {
                transform: translateY(-15px) translateX(5px);
            }
        }
    `;
    document.head.appendChild(style);
});
