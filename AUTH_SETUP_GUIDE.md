# Authentication System Setup Guide

## 🎉 Overview

Complete authentication system with:
- ✅ **Email/Password Authentication**
- ✅ **Google OAuth Integration**
- ✅ **JWT Token Management**
- ✅ **Role-based Access Control**
- ✅ **Session Management**
- ✅ **Beautiful Frontend UI**

---

## 📋 Prerequisites

- PostgreSQL database running (city_mas)
- Python 3.10+ with virtual environment
- Google Cloud Console account (for OAuth)

---

## 🚀 Setup Steps

### 1. Install New Dependencies

```bash
# Navigate to project root
cd D:\City-Governance-System

# Activate virtual environment
.venv\Scripts\activate

# Install new authentication packages
pip install bcrypt PyJWT google-auth google-auth-oauthlib google-auth-httplib2
```

### 2. Run Database Migration

```bash
# Connect to PostgreSQL
psql -U postgres -d city_mas

# Run the authentication schema
\i backend/migrations/auth_schema.sql

# Verify tables created
\dt
# You should see: users, sessions, oauth_tokens, user_preferences, password_reset_tokens

# Exit psql
\q
```

### 3. Configure Google OAuth (Optional but Recommended)

#### Get Google OAuth Credentials:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Google+ API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Configure OAuth consent screen:
   - Application name: "City Governance AI"
   - Authorized domains: localhost
6. Create OAuth Client ID:
   - Application type: **Web application**
   - Authorized JavaScript origins: 
     - `http://localhost:5173`
     - `http://localhost:8000`
   - Authorized redirect URIs:
     - `http://localhost:5173`
     - `http://localhost:8000/api/v1/auth/google`
7. Copy **Client ID** and **Client Secret**

#### Update Backend .env:

Edit `backend/.env`:

```env
# Replace with your actual Google OAuth credentials
GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-actual-client-secret
```

#### Update Frontend Config:

Edit `frontend/js/auth.js` (line 7):

```javascript
const GOOGLE_CLIENT_ID = 'your-actual-client-id.apps.googleusercontent.com';
```

### 4. Update JWT Secret

Edit `backend/.env` and change the JWT secret (already configured):

```env
JWT_SECRET=city-governance-jwt-secret-key-change-in-production-2026
```

**IMPORTANT:** Change this to a random string in production!

```bash
# Generate a random secret (PowerShell)
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | % {[char]$_})
```

---

## 🧪 Testing the Authentication System

### 1. Start the Backend

```bash
# Terminal 1: Start FastAPI backend
cd D:\City-Governance-System
.venv\Scripts\activate
python -m uvicorn backend.app.server:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000

### 2. Start the Frontend

```bash
# Terminal 2: Start Vite frontend
cd D:\City-Governance-System\frontend
npm run dev
```

Frontend will be available at: http://localhost:5173

### 3. Test Registration

1. Open browser: http://localhost:5173/register.html
2. Fill in the form:
   - Full Name: Test User
   - Email: test@example.com
   - Password: Test1234
   - Confirm Password: Test1234
   - Account Type: Citizen
3. Click "Create Account"
4. You should be redirected to home with authentication

### 4. Test Login

1. Open browser: http://localhost:5173/login.html
2. Login with:
   - Email: test@example.com
   - Password: Test1234
3. Click "Sign In"
4. You should be redirected to home

### 5. Test Pre-configured Admin Account

Database includes a default admin account:

- **Email:** admin@citygovernance.in
- **Password:** admin123
- **Role:** admin

### 6. Test Department Users

Database includes department accounts (password: admin123):

- water.dept@citygovernance.in (Water Department)
- fire.dept@citygovernance.in (Fire Department)
- sanitation.dept@citygovernance.in (Sanitation Department)

### 7. Test Google OAuth (if configured)

1. Go to login or register page
2. Click "Sign in with Google" or "Sign up with Google"
3. Select your Google account
4. Authorize the application
5. You should be redirected and logged in

---

## 📚 API Endpoints

All authentication endpoints are available at `http://localhost:8000/api/v1/auth/`

### Register User
```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123",
  "full_name": "John Doe",
  "role": "citizen"
}
```

### Login
```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

### Google OAuth
```bash
POST /api/v1/auth/google
Content-Type: application/json

{
  "id_token": "google-id-token-here"
}
```

### Get Current User
```bash
GET /api/v1/auth/me
Authorization: Bearer your-access-token
```

### Logout
```bash
POST /api/v1/auth/logout
Authorization: Bearer your-access-token
```

### Refresh Token
```bash
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "your-refresh-token"
}
```

### Verify Token
```bash
GET /api/v1/auth/verify
Authorization: Bearer your-access-token
```

---

## 🔒 Security Features

1. **Password Hashing:** bcrypt with salt
2. **JWT Tokens:** HS256 algorithm
3. **Token Expiration:** 
   - Access token: 60 minutes
   - Refresh token: 30 days
4. **Session Tracking:** IP address and user agent
5. **Role-based Access:** citizen, department_user, admin
6. **OAuth Security:** Google token verification

---

## 🎨 Frontend Features

### Login Page (login.html)
- Email/password form
- Google OAuth button
- Remember me checkbox
- Forgot password link
- Animated background
- Glass morphism design

### Register Page (register.html)
- Full registration form
- Password strength indicator
- Role selection (Citizen/Department User)
- Conditional department field
- Google OAuth option
- Terms & conditions checkbox

### Auth JavaScript (auth.js)
- Token storage (localStorage)
- API request wrapper
- Google OAuth integration
- Form validation
- Error handling
- Auto-redirect on success

---

## 🗄️ Database Schema

### users Table
- id (primary key)
- email (unique)
- password_hash
- full_name
- role (citizen, department_user, admin)
- department (water, fire, sanitation, etc.)
- is_active, is_verified
- created_at, updated_at, last_login

### sessions Table
- id (primary key)
- user_id (foreign key)
- token (unique)
- refresh_token
- expires_at
- ip_address, user_agent

### oauth_tokens Table
- id (primary key)
- user_id (foreign key)
- provider (google, github, etc.)
- provider_user_id
- access_token, refresh_token

---

## 🐛 Troubleshooting

### Issue: "Module not found: bcrypt"
**Solution:**
```bash
pip install bcrypt PyJWT google-auth
```

### Issue: Google Sign-In button not working
**Solution:**
1. Check GOOGLE_CLIENT_ID is configured in frontend/js/auth.js
2. Verify Google OAuth credentials in Google Cloud Console
3. Ensure authorized domains include localhost

### Issue: "User already exists" on registration
**Solution:**
- Use a different email or delete the existing user from database:
```sql
DELETE FROM users WHERE email = 'test@example.com';
```

### Issue: CORS errors in browser console
**Solution:**
- Backend .env already includes ALLOWED_ORIGINS
- Make sure backend is running on port 8000
- Frontend should be on port 5173

### Issue: Database connection error
**Solution:**
```bash
# Verify PostgreSQL is running
psql -U postgres -d city_mas -c "SELECT version();"

# Check database credentials in backend/.env
DATABASE_URL=postgresql://postgres:passwordpassword@localhost:5432/city_mas
```

---

## 📱 Next Steps

### Optional Enhancements:

1. **Email Verification:**
   - Implement email sending
   - Add verification token flow
   - Update is_verified flag

2. **Password Reset:**
   - Email reset link
   - Token validation
   - Password update flow

3. **Multi-factor Authentication:**
   - TOTP implementation
   - SMS verification
   - Backup codes

4. **Social Login:**
   - GitHub OAuth
   - Microsoft OAuth
   - LinkedIn OAuth

5. **Advanced Features:**
   - Account lockout after failed attempts
   - Password history
   - Session management UI
   - Audit logs

---

## ✅ Verification Checklist

- [ ] Database migration completed
- [ ] Dependencies installed
- [ ] Backend .env configured
- [ ] Frontend auth.js updated with Google Client ID
- [ ] Backend server running on port 8000
- [ ] Frontend server running on port 5173
- [ ] Can register new user
- [ ] Can login with email/password
- [ ] Can login with admin account
- [ ] Google OAuth configured (optional)
- [ ] Tokens stored in localStorage
- [ ] Logout clears authentication

---

## 🎯 Production Deployment

Before deploying to production:

1. **Change JWT_SECRET** to a cryptographically secure random string
2. **Update GOOGLE_CLIENT_ID** with production domain
3. **Enable HTTPS** for OAuth and token security
4. **Set secure cookie flags** in production
5. **Implement rate limiting** on auth endpoints
6. **Add email verification** for new registrations
7. **Enable database SSL** connections
8. **Configure CORS** for production domain only
9. **Add monitoring** for failed login attempts
10. **Backup database** regularly

---

## 📞 Support

For issues or questions:
- Check troubleshooting section above
- Review API documentation
- Verify database schema is correctly applied
- Ensure all environment variables are set

---

**Status:** ✅ Authentication system complete and ready for testing!
