// Interactive Elements and User Interactions
class InteractiveElements {
    constructor() {
        this.init();
    }
    
    init() {
        this.setupAgentOrbs();
        this.setupSearchInterface();
        this.setupCTAButtons();
        this.setupNavigation();
    }
    
    // Agent Orbs Interactions
    setupAgentOrbs() {
        const orbs = document.querySelectorAll('.agent-orb');
        const centralNode = document.querySelector('.coordination-core');
        
        orbs.forEach(orb => {
            orb.addEventListener('click', () => {
                // Pulse effect on central node
                if (centralNode) {
                    centralNode.style.animation = 'none';
                    setTimeout(() => {
                        centralNode.style.animation = 'pulse 3s ease-in-out infinite, ripple 2s ease-out infinite';
                    }, 10);
                }
                
                // Show connection animation
                this.animateConnection(orb);
            });
        });
    }
    
    animateConnection(orb) {
        const connection = orb.querySelector('.connection-line');
        if (!connection) return;
        
        connection.style.animation = 'none';
        setTimeout(() => {
            connection.style.animation = 'connectionPulse 0.6s ease-out';
        }, 10);
    }
    
    // Search Interface
    setupSearchInterface() {
        const searchInput = document.getElementById('semantic-search');
        const crystals = document.querySelectorAll('.crystal');
        
        if (!searchInput) return;
        
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            
            crystals.forEach(crystal => {
                const type = crystal.getAttribute('data-type');
                
                if (query && type && type.includes(query)) {
                    crystal.style.transform = `
                        translateX(calc(var(--x) * 1px)) 
                        translateY(calc(var(--y) * 1px - 20px)) 
                        translateZ(calc(var(--z) * 1px)) 
                        scale(1.5)
                    `;
                    crystal.style.opacity = '1';
                    crystal.style.filter = 'brightness(1.5)';
                } else {
                    crystal.style.transform = `
                        translateX(calc(var(--x) * 1px)) 
                        translateY(calc(var(--y) * 1px)) 
                        translateZ(calc(var(--z) * 1px))
                        scale(1)
                    `;
                    crystal.style.opacity = query ? '0.3' : '1';
                    crystal.style.filter = 'brightness(1)';
                }
            });
        });
    }
    
    // CTA Buttons
    setupCTAButtons() {
        const ctaButtons = document.querySelectorAll('.cta-primary, .cta-secondary');
        
        ctaButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                // Ripple effect
                const ripple = document.createElement('span');
                const rect = button.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;
                
                ripple.style.cssText = `
                    position: absolute;
                    width: ${size}px;
                    height: ${size}px;
                    border-radius: 50%;
                    background: rgba(255, 255, 255, 0.5);
                    left: ${x}px;
                    top: ${y}px;
                    transform: scale(0);
                    animation: rippleEffect 0.6s ease-out;
                    pointer-events: none;
                `;
                
                button.appendChild(ripple);
                
                setTimeout(() => ripple.remove(), 600);
            });
        });
        
        // Add ripple animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes rippleEffect {
                to {
                    transform: scale(2);
                    opacity: 0;
                }
            }
            
            @keyframes connectionPulse {
                0% { opacity: 0.3; transform: scaleY(1); }
                50% { opacity: 1; transform: scaleY(1.2); }
                100% { opacity: 0.3; transform: scaleY(1); }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Smooth Navigation
    setupNavigation() {
        const navLinks = document.querySelectorAll('.nav-link, a[href^="#"]');
        
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                const href = link.getAttribute('href');
                
                if (href && href.startsWith('#')) {
                    e.preventDefault();
                    const target = document.querySelector(href);
                    
                    if (target) {
                        target.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                }
            });
        });
    }
}

// Accessibility Controls
class AccessibilityControls {
    constructor() {
        this.reducedMotion = false;
        this.highContrast = false;
        this.init();
    }
    
    init() {
        // Reduced Motion Toggle
        const reduceMotionBtn = document.getElementById('reduce-motion');
        if (reduceMotionBtn) {
            reduceMotionBtn.addEventListener('click', () => {
                this.reducedMotion = !this.reducedMotion;
                document.body.classList.toggle('reduced-motion', this.reducedMotion);
                
                if (this.reducedMotion) {
                    reduceMotionBtn.innerHTML = '<span class="icon">🐌</span>';
                } else {
                    reduceMotionBtn.innerHTML = '<span class="icon">⚡</span>';
                }
            });
        }
        
        // High Contrast Toggle
        const highContrastBtn = document.getElementById('high-contrast');
        if (highContrastBtn) {
            highContrastBtn.addEventListener('click', () => {
                this.highContrast = !this.highContrast;
                document.body.classList.toggle('high-contrast', this.highContrast);
                
                if (this.highContrast) {
                    highContrastBtn.innerHTML = '<span class="icon">◑</span>';
                } else {
                    highContrastBtn.innerHTML = '<span class="icon">◐</span>';
                }
            });
        }
        
        // Check user preference for reduced motion
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            this.reducedMotion = true;
            document.body.classList.add('reduced-motion');
            if (reduceMotionBtn) {
                reduceMotionBtn.innerHTML = '<span class="icon">🐌</span>';
            }
        }
    }
}

// Pipeline Animation
class PipelineAnimation {
    constructor() {
        this.nodes = document.querySelectorAll('.pipeline-node');
        this.init();
    }
    
    init() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.animatePipeline();
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.3 });
        
        if (this.nodes.length > 0) {
            observer.observe(this.nodes[0]);
        }
    }
    
    animatePipeline() {
        this.nodes.forEach((node, index) => {
            setTimeout(() => {
                node.style.opacity = '1';
                node.style.transform = 'translateY(0)';
            }, index * 150);
        });
    }
}

// Initialize all interactions
document.addEventListener('DOMContentLoaded', () => {
    new InteractiveElements();
    new AccessibilityControls();
    new PipelineAnimation();
});

// Handle window resize
let resizeTimeout;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
        // Reinitialize elements that need resize handling
        console.log('Window resized, recalculating layouts...');
    }, 250);
});
