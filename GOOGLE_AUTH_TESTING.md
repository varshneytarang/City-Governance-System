# Google OAuth Testing Guide

## ✅ Completed Setup

### Frontend Changes
1. **index.html** - Added Google Sign-In library
   - Script: `https://accounts.google.com/gsi/client`

2. **Login.jsx** - Google OAuth fully integrated
   - Google Client ID configured
   - OAuth initialization in useEffect
   - `handleGoogleCallback` function for token processing
   - Google Sign-In button container with ID: `google-signin-button`

3. **Register.jsx** - Google OAuth fully integrated
   - Google Client ID configured
   - OAuth initialization in useEffect
   - `handleGoogleCallback` function for token processing
   - Google Sign-In button container with ID: `google-register-button`

### Backend Configuration
1. **backend/.env** - Google Client ID set
   ```
   GOOGLE_CLIENT_ID=991760266088-86h3t0h18dffgautu20mgiteboa8t9ln.apps.googleusercontent.com
   ```

2. **auth_server.py** - CORS configured for:
   - `http://localhost:3000` ✅
   - `http://localhost:5173` ✅
   - `http://127.0.0.1:3000` ✅
   - `http://127.0.0.1:5173` ✅

3. **backend/app/routes/auth.py** - Google OAuth endpoint ready
   - Route: `POST /api/v1/auth/google`
   - Accepts: `{ id_token: string }`
   - Returns: User data + JWT tokens

## 🧪 Testing Steps

### Step 1: Restart Backend Server (If Running)
```powershell
# Stop existing server (Ctrl+C in terminal)
# Then restart:
python auth_server.py
```

### Step 2: Restart Frontend (If Running)
```powershell
# In frontend directory:
npm run dev
```
The dev server should be on http://localhost:3000

### Step 3: Test Google Sign-In on Login Page
1. Open http://localhost:3000/login
2. You should see:
   - Email/password form
   - "or continue with" divider
   - **Google Sign-In button** (blue Google button)
3. Click the Google button
4. Complete Google OAuth flow in popup
5. After success, you should be redirected to homepage with your username showing

### Step 4: Test Google Sign-In on Register Page
1. Open http://localhost:3000/register
2. You should see:
   - Registration form
   - "or sign up with" divider
   - **Google Sign-In button** (blue Google button)
3. Click the Google button
4. Complete Google OAuth flow
5. After success, you should be redirected to homepage with your username showing

## 🔍 Troubleshooting

### If Google Button Doesn't Appear
1. **Check Browser Console** (F12 → Console tab)
   - Look for errors with `google.accounts.id`
   - Error "google is not defined" means script didn't load

2. **Verify Script Loading**
   - Open DevTools → Network tab
   - Filter by "gsi"
   - You should see `https://accounts.google.com/gsi/client` loaded (200 OK)

3. **Hard Refresh**
   - Press `Ctrl + Shift + R` to clear cache and reload
   - This ensures the new index.html with Google script is loaded

### If "Google Sign-In is not available" Error
This error means the Google library loaded but initialization failed:
1. Check that GOOGLE_CLIENT_ID in Login.jsx and Register.jsx matches backend/.env
2. Verify Google Client ID is valid in Google Cloud Console
3. Check browser console for specific errors

### CORS Errors
If you see CORS errors in console:
1. **Verify Backend Running**: Check http://localhost:8000/health returns `{"status":"healthy"}`
2. **Check CORS Headers**: 
   - Open Network tab in DevTools
   - Make a request to /api/v1/auth/register
   - Click on request → Headers tab
   - Look for `Access-Control-Allow-Origin: http://localhost:3000`
3. **Restart Backend**: Sometimes CORS middleware needs server restart

## ✨ Expected Behavior

### Successful Google Login Flow:
1. Click "Sign in with Google" button
2. Google popup opens asking to choose account
3. Select your Google account
4. Popup closes automatically
5. Backend receives ID token
6. Backend verifies token with Google
7. Backend creates/retrieves user account
8. Backend returns JWT tokens
9. Frontend stores tokens in localStorage
10. Frontend redirects to homepage (/)
11. Username appears in top-right with Logout button

### What Happens on Backend:
1. Receives `id_token` from frontend
2. Verifies token with Google's servers
3. Extracts user info (email, name, Google ID, picture)
4. Checks if user exists with this Google ID in database
5. If exists: returns existing user
6. If new: creates new user account with `auth_provider: "google"`
7. Generates JWT access + refresh tokens
8. Returns user data + tokens to frontend

## 📝 Notes

- **Google OAuth** doesn't require password - authentication is handled by Google
- Users created via Google OAuth have `auth_provider = "google"` in database
- Google users can't login with email/password (no password stored)
- CORS is configured to allow credentials (cookies/headers) from localhost:3000

## 🎯 Success Criteria

✅ Google button renders on both Login and Register pages  
✅ Clicking button opens Google account selector  
✅ After selecting account, redirects to homepage  
✅ Username displays in top-right corner  
✅ No CORS errors in browser console  
✅ User account created in database (check with SQL query if needed)

---

## Quick Commands Reference

### Check if auth server is running:
```powershell
# Windows
netstat -ano | findstr :8000
```

### Test auth endpoint manually:
```powershell
# Windows PowerShell
Invoke-WebRequest -Uri http://localhost:8000/health
```

### Kill process on port 8000 (if needed):
```powershell
# Find PID
netstat -ano | findstr :8000
# Kill (replace PID with actual number)
taskkill /PID <PID> /F
```

### Start fresh:
```powershell
# Terminal 1 - Backend
python auth_server.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```
