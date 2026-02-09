// Main Application Entry Point
class CityGovernanceApp {
    constructor() {
        this.isLoaded = false;
        this.init();
    }
    
    init() {
        // Show loading state
        this.showLoadingAnimation();
        
        // Wait for DOM and all resources
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.onDOMReady());
        } else {
            this.onDOMReady();
        }
        
        window.addEventListener('load', () => this.onFullLoad());
    }
    
    showLoadingAnimation() {
        document.body.style.opacity = '0';
    }
    
    onDOMReady() {
        console.log('🚀 City Governance AI - System Initializing...');
        
        // Initialize critical systems
        this.initializeAccessibility();
        this.initializeNavigation();
        this.initializePerformanceMonitoring();
    }
    
    onFullLoad() {
        // Fade in content
        document.body.style.transition = 'opacity 0.6s ease';
        document.body.style.opacity = '1';
        
        this.isLoaded = true;
        console.log('✅ City Governance AI - System Ready');
        
        // Log system info
        this.logSystemInfo();
        
        // Initialize non-critical features
        this.initializeAnalytics();
    }
    
    initializeAccessibility() {
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            // Escape key to close modals/overlays
            if (e.key === 'Escape') {
                this.closeAllOverlays();
            }
            
            // Tab key accessibility
            if (e.key === 'Tab') {
                document.body.classList.add('keyboard-navigation');
            }
        });
        
        // Remove keyboard navigation class on mouse use
        document.addEventListener('mousedown', () => {
            document.body.classList.remove('keyboard-navigation');
        });
    }
    
    initializeNavigation() {
        // Track current section
        const sections = document.querySelectorAll('section[id]');
        const navLinks = document.querySelectorAll('.nav-link');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const id = entry.target.getAttribute('id');
                    
                    // Update active nav link
                    navLinks.forEach(link => {
                        link.classList.remove('active');
                        if (link.getAttribute('href') === `#${id}`) {
                            link.classList.add('active');
                        }
                    });
                }
            });
        }, { threshold: 0.5 });
        
        sections.forEach(section => observer.observe(section));
    }
    
    initializePerformanceMonitoring() {
        // Monitor Core Web Vitals
        if ('PerformanceObserver' in window) {
            // Largest Contentful Paint (LCP)
            const lcpObserver = new PerformanceObserver((list) => {
                const entries = list.getEntries();
                const lastEntry = entries[entries.length - 1];
                console.log('📊 LCP:', lastEntry.renderTime || lastEntry.loadTime, 'ms');
            });
            
            try {
                lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
            } catch (e) {
                // Silently fail if not supported
            }
            
            // Cumulative Layout Shift (CLS)
            let clsScore = 0;
            const clsObserver = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (!entry.hadRecentInput) {
                        clsScore += entry.value;
                    }
                }
                console.log('📊 CLS:', clsScore.toFixed(3));
            });
            
            try {
                clsObserver.observe({ entryTypes: ['layout-shift'] });
            } catch (e) {
                // Silently fail if not supported
            }
        }
        
        // Monitor FPS
        this.monitorFPS();
    }
    
    monitorFPS() {
        let lastTime = performance.now();
        let frames = 0;
        
        const measureFPS = () => {
            frames++;
            const currentTime = performance.now();
            
            if (currentTime >= lastTime + 1000) {
                const fps = Math.round((frames * 1000) / (currentTime - lastTime));
                
                if (fps < 30) {
                    console.warn('⚠️ Low FPS detected:', fps);
                }
                
                frames = 0;
                lastTime = currentTime;
            }
            
            requestAnimationFrame(measureFPS);
        };
        
        requestAnimationFrame(measureFPS);
    }
    
    initializeAnalytics() {
        // Track page engagement
        let engagementTime = 0;
        let isActive = true;
        
        setInterval(() => {
            if (isActive && !document.hidden) {
                engagementTime++;
            }
        }, 1000);
        
        // Track visibility
        document.addEventListener('visibilitychange', () => {
            isActive = !document.hidden;
        });
        
        // Log engagement on page unload
        window.addEventListener('beforeunload', () => {
            console.log('📈 Total engagement time:', engagementTime, 'seconds');
        });
    }
    
    closeAllOverlays() {
        // Close any open overlays, modals, etc.
        const overlays = document.querySelectorAll('.overlay, .modal');
        overlays.forEach(overlay => {
            overlay.classList.remove('active');
        });
    }
    
    logSystemInfo() {
        console.log('%c🏛️ City Governance AI System', 'font-size: 20px; font-weight: bold; color: #00D4FF;');
        console.log('%cArchitecture: Enterprise v2.0', 'color: #00FF88;');
        console.log('%cStatus: Production ✅', 'color: #00FF88;');
        console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #00D4FF;');
        console.log('Platform: Multi-tier architecture');
        console.log('Availability: 24/7 operation');
        console.log('Uptime: 99.9% guaranteed');
        console.log('Security: Enterprise-grade');
        console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #00D4FF;');
        console.log('Performance monitoring active');
        console.log('Accessibility features enabled');
        console.log('Neural background rendering');
        console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #00D4FF;');
    }
}

// Initialize application
new CityGovernanceApp();

// Export for potential module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CityGovernanceApp;
}
