// Custom Cursor with Particle Trail
class CustomCursor {
    constructor() {
        this.cursor = document.querySelector('.custom-cursor');
        this.trail = document.querySelector('.cursor-trail');
        this.cursorPos = { x: 0, y: 0 };
        this.trailPos = { x: 0, y: 0 };
        
        this.init();
    }
    
    init() {
        // Update cursor position
        document.addEventListener('mousemove', (e) => {
            this.cursorPos.x = e.clientX;
            this.cursorPos.y = e.clientY;
        });
        
        // Animate cursor and trail
        this.animate();
        
        // Interactive elements
        this.addInteractiveStates();
    }
    
    animate() {
        // Smooth cursor movement
        this.cursor.style.left = `${this.cursorPos.x}px`;
        this.cursor.style.top = `${this.cursorPos.y}px`;
        
        // Trail follows with delay
        this.trailPos.x += (this.cursorPos.x - this.trailPos.x) * 0.15;
        this.trailPos.y += (this.cursorPos.y - this.trailPos.y) * 0.15;
        
        this.trail.style.left = `${this.trailPos.x}px`;
        this.trail.style.top = `${this.trailPos.y}px`;
        
        requestAnimationFrame(() => this.animate());
    }
    
    addInteractiveStates() {
        const interactiveElements = document.querySelectorAll('a, button, .agent-orb, .stat-card');
        
        interactiveElements.forEach(element => {
            element.addEventListener('mouseenter', () => {
                this.cursor.style.transform = 'scale(2)';
                this.cursor.style.borderColor = 'var(--accent-secondary)';
            });
            
            element.addEventListener('mouseleave', () => {
                this.cursor.style.transform = 'scale(1)';
                this.cursor.style.borderColor = 'var(--accent-primary)';
            });
        });
    }
}

// Initialize cursor if not on mobile
if (window.innerWidth > 768) {
    document.addEventListener('DOMContentLoaded', () => {
        new CustomCursor();
    });
}
