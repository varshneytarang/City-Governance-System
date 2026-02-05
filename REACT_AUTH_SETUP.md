# React Authentication Pages - Setup Guide

## Overview
The login and register pages have been converted to React components with a modern two-column layout featuring government-themed animations.

## New Files Created

### Components
1. **Login.jsx** - Login page with two-column layout
2. **Register.jsx** - Registration page with two-column layout
3. **GovernmentAnimation.jsx** - Reusable animation component with:
   - Animated particle network
   - City buildings with blinking windows
   - Government shield logo
   - Data flow visualization
   - Agent network nodes
   - Floating documents

### Styles
4. **auth.css** - Complete styling for authentication pages

## Features

### Login Page (`/#login`)
- **Left Side**: 
  - Email/password form
  - Remember me checkbox
  - Forgot password link
  - Google Sign-In button
  - Link to registration
- **Right Side**:
  - Government-themed animation
  - "Secure Access" message
  - Particle network visualization
  - Data flow animation

### Register Page (`/#register`)
- **Left Side**:
  - Full name, email, password fields
  - Password strength indicator (5 levels)
  - Confirm password validation
  - Account type selector (Citizen/Department User)
  - Department dropdown (for department users)
  - Terms & conditions checkbox
  - Google Sign-Up button
  - Link to login
- **Right Side**:
  - Government-themed animation
  - "Join the Network" message
  - Agent network visualization
  - Floating documents

## Navigation

The app now supports hash-based routing:

- `http://localhost:5173/` or `/#home` - Main landing page
- `http://localhost:5173/#login` - Login page
- `http://localhost:5173/#register` - Registration page
- `http://localhost:5173/#test` - API test console

## Layout Design

### Two-Column Layout
```
┌─────────────────────────────────────────────────────────┐
│  Form Side (50%)          │  Animation Side (50%)       │
│  ─────────────            │  ─────────────────────      │
│  Logo & Title             │  Particle Network           │
│  Input Fields             │  City Buildings             │
│  Validation               │  Government Logo            │
│  Buttons                  │  Data Visualizations        │
│  Links                    │  Animated Elements          │
└─────────────────────────────────────────────────────────┘
```

### Responsive Design
- **Desktop (>1024px)**: Side-by-side layout
- **Tablet (<1024px)**: Stacked layout with animation on top
- **Mobile (<640px)**: Simplified layout with smaller animations

## Government Animation Types

### Login Animation
- Particle network
- City buildings with window lights
- Government shield logo
- Vertical data flow lines
- "Secure Access" overlay

### Register Animation
- Particle network
- City buildings
- Government shield logo
- Agent network nodes with pulse effects
- "Join the Network" overlay

## API Integration

Both pages integrate with the existing FastAPI backend:

### Login Endpoint
```javascript
POST http://localhost:8000/api/v1/auth/login
Body: { email, password }
Response: { token, user }
```

### Register Endpoint
```javascript
POST http://localhost:8000/api/v1/auth/register
Body: { email, password, full_name, role, department? }
Response: { token, user }
```

### Google OAuth
```javascript
POST http://localhost:8000/api/v1/auth/google
Body: { credential }
Response: { token, user }
```

## Authentication Flow

1. User fills form on Login/Register page
2. Form validation (client-side)
3. API call to backend
4. Backend validates and creates/verifies user
5. JWT tokens returned
6. Tokens stored in localStorage:
   - `city_governance_token` - Access token
   - `city_governance_refresh_token` - Refresh token
   - `city_governance_user` - User info (JSON)
7. Redirect to home page on success

## Password Strength Indicator (Register)

The register page includes a visual password strength meter:
- **Level 1 (Red)**: Very Weak
- **Level 2 (Orange)**: Weak
- **Level 3 (Yellow)**: Fair
- **Level 4 (Light Green)**: Good
- **Level 5 (Green)**: Strong

Criteria:
- Length ≥ 8 characters
- Contains uppercase letter
- Contains lowercase letter
- Contains number
- Contains special character

## Error Handling

Both pages display animated error/success alerts:
- **Error Alert**: Red background with error message
- **Success Alert**: Green background with success message
- **Auto-dismiss**: Success messages auto-redirect after 1.5s
- **Manual dismiss**: Error messages have close button

## Animations

### Framer Motion Animations
- **Page Entry**: Slide in from left (form) and right (animation)
- **Form Elements**: Fade in with stagger
- **Alerts**: Slide down from top
- **Buttons**: Scale on hover
- **Loading State**: Spinning loader

### Canvas Animations
- Particle system with connection lines
- Smooth interpolation
- 60 FPS performance
- Responsive to window size

## Styling Details

### Color Palette
- **Background**: Dark gradient (#0f172a to #1e293b)
- **Primary**: Blue gradient (#3b82f6 to #8b5cf6)
- **Text**: Light shades (#f8fafc, #e2e8f0)
- **Accents**: Blue (#3b82f6)

### Effects
- **Glassmorphism**: Backdrop blur on inputs
- **Glow**: Box shadows on buttons and elements
- **Gradients**: Text and button gradients
- **Transitions**: Smooth 0.3s transitions

## Running the Application

1. **Start Backend** (if not already running):
```bash
cd backend
python -m uvicorn app.main:app --reload
```

2. **Start Frontend** (if not already running):
```bash
cd frontend
npm run dev
```

3. **Navigate**:
- Home: http://localhost:5173/
- Login: http://localhost:5173/#login
- Register: http://localhost:5173/#register

## Testing

### Test Accounts (from auth_schema.sql)
```
Email: admin@citygovernance.in
Password: admin123
Role: Admin

Email: fire.dept@citygovernance.in
Password: admin123
Role: Department User (Fire)

Email: water.dept@citygovernance.in
Password: admin123
Role: Department User (Water)

Email: sanitation.dept@citygovernance.in
Password: admin123
Role: Department User (Sanitation)
```

## Next Steps

1. **Protected Routes**: Add authentication middleware
2. **Dashboard**: Create user dashboard component
3. **Profile**: Add user profile page
4. **Password Reset**: Implement forgot password flow
5. **Email Verification**: Add email verification
6. **Session Management**: Add auto-logout on token expiry

## Dependencies

All dependencies are already in your project:
- React 18
- Framer Motion
- Tailwind CSS (or custom CSS)
- FastAPI (backend)
- PostgreSQL (backend)

## Notes

- The old HTML pages (login.html, register.html, dashboard.html) can be kept for reference or deleted
- The auth.js file can be kept for reference but is no longer needed for React
- Google OAuth requires configuration in the backend (CLIENT_ID environment variable)
- CORS is configured in backend to allow frontend requests

## Troubleshooting

**Issue**: Animation not showing
- **Solution**: Check that auth.css is imported correctly

**Issue**: Login/Register not working
- **Solution**: Verify backend is running on port 8000

**Issue**: Google Sign-In not working
- **Solution**: Check GOOGLE_CLIENT_ID in backend .env file

**Issue**: Styling looks broken
- **Solution**: Ensure auth.css is loaded and no CSS conflicts

## Support

For issues or questions, check:
1. Browser console for errors
2. Backend logs for API errors
3. Network tab for failed requests
4. React DevTools for component state
