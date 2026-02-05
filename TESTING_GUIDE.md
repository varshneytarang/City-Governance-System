# Complete Setup & Testing Guide for Login/Register Pages

## ✅ Prerequisites Check

Your current setup status:
- ✅ **Backend**: Running on http://localhost:8000
- ✅ **Frontend**: Running on http://localhost:3000
- ⏳ **Database**: Need to run auth_schema.sql

---

## 📋 Step-by-Step Setup

### **STEP 1: Set Up Database Tables**

Run the authentication schema to create tables and test accounts:

```powershell
# Option A: Using psql command line
psql -U postgres -d city_governance -f "D:\City-Governance-System\backend\migrations\auth_schema.sql"

# Option B: Using pgAdmin
# 1. Open pgAdmin
# 2. Connect to your PostgreSQL server
# 3. Open city_governance database
# 4. Go to Query Tool
# 5. Open file: D:\City-Governance-System\backend\migrations\auth_schema.sql
# 6. Click Execute (F5)
```

**Expected Result**: 5 tables created (users, sessions, oauth_tokens, user_preferences, password_reset_tokens) + 4 test accounts inserted

---

### **STEP 2: Verify Backend is Running**

Your backend is already running! Verify it's accessible:

```powershell
# Test backend health
curl http://localhost:8000/health

# Expected response: {"status": "healthy"}
```

**Check these files exist:**
- ✅ `backend/app/routes/auth.py` - Auth endpoints
- ✅ `backend/app/auth_utils.py` - Auth utilities
- ✅ `backend/app/auth_schemas.py` - Pydantic models

---

### **STEP 3: Verify Frontend is Running**

Your frontend is already running on http://localhost:3000!

**Check these files exist:**
- ✅ `frontend/src/components/Login.jsx`
- ✅ `frontend/src/components/Register.jsx`
- ✅ `frontend/src/components/GovernmentAnimation.jsx`
- ✅ `frontend/src/styles/auth.css`

---

### **STEP 4: Import auth.css in Main App**

Ensure the auth styles are loaded:

**Check if auth.css is imported in `frontend/src/main.jsx` or `frontend/src/index.css`:**

```jsx
// Add this import to frontend/src/main.jsx
import './styles/auth.css'
```

---

## 🧪 Testing the Pages

### **Test 1: Access Login Page**

1. Open browser: **http://localhost:3000/#login**
2. **Expected**: 
   - Two-column layout
   - Form on left with email/password fields
   - Animated government visualization on right
   - Buildings with blinking windows
   - Particle network
   - Blue/purple gradient theme

---

### **Test 2: Access Register Page**

1. Open browser: **http://localhost:3000/#register**
2. **Expected**:
   - Two-column layout
   - Extended form on left with all registration fields
   - Different animation on right (agent network)
   - Password strength indicator

---

### **Test 3: Login with Test Account**

**Use Pre-configured Test Accounts:**

```
Admin Account:
Email: admin@citygovernance.in
Password: admin123

Fire Department:
Email: fire.dept@citygovernance.in
Password: admin123

Water Department:
Email: water.dept@citygovernance.in
Password: admin123

Sanitation Department:
Email: sanitation.dept@citygovernance.in
Password: admin123
```

**Steps:**
1. Go to http://localhost:3000/#login
2. Enter email: `admin@citygovernance.in`
3. Enter password: `admin123`
4. Click "Sign In"
5. **Expected**: 
   - Green success message: "Login successful! Redirecting..."
   - Auto-redirect to home page after 1.5 seconds
   - Token stored in localStorage

**Verify Login Success:**
Open browser console (F12) and run:
```javascript
// Check if tokens are stored
console.log(localStorage.getItem('city_governance_token'))
console.log(localStorage.getItem('city_governance_user'))
```

---

### **Test 4: Register New User (Citizen)**

**Steps:**
1. Go to http://localhost:3000/#register
2. Fill form:
   - Full Name: `John Citizen`
   - Email: `john.citizen@gmail.com`
   - Password: `SecurePass123!`
   - Confirm Password: `SecurePass123!`
   - Account Type: `Citizen` (default)
   - Check "Terms & Conditions"
3. Watch password strength indicator change colors
4. Click "Create Account"
5. **Expected**:
   - Green success message
   - Auto-redirect to home
   - Account created in database

---

### **Test 5: Register Department User**

**Steps:**
1. Go to http://localhost:3000/#register
2. Fill form:
   - Full Name: `Jane Engineer`
   - Email: `jane.engineer@citygovernance.in`
   - Password: `EngineerPass123!`
   - Confirm Password: `EngineerPass123!`
   - Account Type: Select `Department User`
   - Department: Select `Engineering` (dropdown appears)
   - Check "Terms & Conditions"
3. Click "Create Account"
4. **Expected**: Department user created with engineering role

---

### **Test 6: Form Validations**

**Test Password Mismatch:**
1. Register page
2. Password: `Test123!`
3. Confirm: `Different123!`
4. Click submit
5. **Expected**: Red error: "Passwords do not match"

**Test Missing Terms:**
1. Fill all fields
2. Don't check "Terms & Conditions"
3. Click submit
4. **Expected**: Red error: "Please accept the terms and conditions"

**Test Missing Department:**
1. Select "Department User"
2. Don't select department
3. Click submit
4. **Expected**: Red error: "Please select a department"

**Test Weak Password:**
1. Enter password: `123`
2. **Expected**: Strength indicator shows "Very Weak" in red

**Test Strong Password:**
1. Enter password: `MySecure123!Pass`
2. **Expected**: Strength indicator shows "Strong" in green

---

### **Test 7: Navigation Between Pages**

**From Login to Register:**
1. Go to login page
2. Click "Sign up" link at bottom
3. **Expected**: Navigate to register page

**From Register to Login:**
1. Go to register page
2. Click "Sign in" link at bottom
3. **Expected**: Navigate to login page

**Back to Home:**
1. On any auth page
2. Click "← Back to Home" link
3. **Expected**: Navigate to main landing page

---

### **Test 8: API Error Handling**

**Test Invalid Login:**
1. Login page
2. Email: `wrong@email.com`
3. Password: `wrongpass`
4. Click "Sign In"
5. **Expected**: Red error: "Invalid email or password"

**Test Duplicate Email:**
1. Register page
2. Email: `admin@citygovernance.in` (already exists)
3. Fill other fields
4. Click "Create Account"
5. **Expected**: Red error: "Email already registered"

---

### **Test 9: Loading States**

**Test Button Disabled During Submit:**
1. Fill login form
2. Click "Sign In"
3. **Expected**: 
   - Button shows spinner
   - Button is disabled
   - Cannot click multiple times

---

### **Test 10: Responsive Design**

**Test Mobile View:**
1. Open browser DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Select iPhone or mobile device
4. Navigate to login/register
5. **Expected**:
   - Form on top
   - Animation below
   - Vertical stacking
   - Touch-friendly buttons

**Test Tablet View:**
1. Set viewport to iPad
2. **Expected**: Stacked layout, larger than mobile

---

## 🔍 Verification Commands

### **Check Database Tables:**
```sql
-- Connect to PostgreSQL
psql -U postgres -d city_governance

-- Verify tables exist
\dt

-- Check users table
SELECT id, email, full_name, role FROM users;

-- Check sessions table
SELECT * FROM sessions;
```

### **Check Backend Logs:**
Look at your PowerShell terminal running uvicorn:
- Should show POST requests to `/api/v1/auth/login` or `/api/v1/auth/register`
- Status codes: 200 (success) or 400/422 (validation error)

### **Check Browser Console:**
Open DevTools (F12) → Console tab:
- Should NOT see any red errors
- Check Network tab for API calls
- Status 200 = success
- Status 400/422 = validation error

### **Check localStorage:**
```javascript
// In browser console
localStorage.getItem('city_governance_token')
localStorage.getItem('city_governance_refresh_token')
localStorage.getItem('city_governance_user')

// Clear tokens (logout)
localStorage.clear()
```

---

## 🎨 Visual Checks

### **Login Page Should Show:**
- ✅ Blue government building icon logo
- ✅ "Welcome Back" title
- ✅ Email and password inputs with glass effect
- ✅ "Remember me" checkbox
- ✅ "Forgot password?" link
- ✅ Blue gradient "Sign In" button
- ✅ Google sign-in button with Google logo
- ✅ Animated city buildings on right
- ✅ Particle network connections
- ✅ Data flow vertical lines
- ✅ "Secure Access" overlay text

### **Register Page Should Show:**
- ✅ Government building icon logo
- ✅ "Create Account" title
- ✅ 6 input fields (name, email, password, confirm, role, department)
- ✅ Password strength bar (changes color)
- ✅ Department dropdown (only if "Department User" selected)
- ✅ Terms checkbox
- ✅ Blue gradient "Create Account" button
- ✅ Google sign-up button
- ✅ Agent network nodes on right (pulsing circles)
- ✅ "Join the Network" overlay text

---

## ⚙️ Configuration Checklist

Before testing, ensure these are configured:

### **Backend (.env file):**
```bash
# Required for auth
DATABASE_URL=postgresql://postgres:passwordpassword@localhost:5432/city_mas
JWT_SECRET=city-governance-jwt-secret-key-change-in-production-2026
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# Optional for Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id-here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret-here

# CORS - should include frontend URL
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### **Backend Routes Registered:**
Check `backend/app/server.py` or `backend/app/main.py` includes auth routes:
```python
from app.routes import auth
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
```

---

## 🐛 Troubleshooting

### **Issue: "Failed to fetch" error**
**Solution:** 
- Check backend is running on port 8000
- Check CORS settings in backend
- Verify DATABASE_URL in .env

### **Issue: Animations not showing**
**Solution:**
- Check auth.css is imported
- Check browser console for errors
- Try hard refresh (Ctrl+Shift+R)

### **Issue: Google Sign-In button does nothing**
**Solution:**
- Google OAuth requires GOOGLE_CLIENT_ID in .env
- Need to set up Google Cloud Console project
- For now, use email/password login

### **Issue: "Database error" on login**
**Solution:**
- Run auth_schema.sql to create tables
- Check PostgreSQL is running
- Verify database connection string

### **Issue: Password strength not showing**
**Solution:**
- Type in password field
- Should appear as you type
- Check browser console for JS errors

### **Issue: Page is blank**
**Solution:**
- Check browser console for errors
- Verify all components are imported in App.jsx
- Check auth.css exists

---

## 📊 Success Criteria

You'll know everything works when:

1. ✅ Login page loads with two-column layout
2. ✅ Register page loads with two-column layout
3. ✅ Animations are visible and smooth
4. ✅ Can login with test account (admin@citygovernance.in)
5. ✅ Tokens appear in localStorage after login
6. ✅ Can register new user
7. ✅ Form validations show error messages
8. ✅ Password strength indicator changes colors
9. ✅ Navigation between pages works
10. ✅ Redirects to home after successful auth

---

## 🚀 Quick Start (TL;DR)

```powershell
# 1. Create database tables (run once)
psql -U postgres -d city_governance -f "backend/migrations/auth_schema.sql"

# 2. Backend already running ✅

# 3. Frontend already running ✅

# 4. Test login
# Browser: http://localhost:3000/#login
# Email: admin@citygovernance.in
# Password: admin123

# 5. Test register
# Browser: http://localhost:3000/#register
# Fill form and submit
```

---

## 📝 Notes

- Frontend running on: **http://localhost:3000**
- Backend API on: **http://localhost:8000**
- API Docs: **http://localhost:8000/docs**
- Hash routing: Use `#login` and `#register` in URL
- Test accounts have password: `admin123`
- Tokens expire after 60 minutes (configurable in .env)

---

## 🎯 Next Steps After Testing

Once login/register works:
1. Create protected routes (require login)
2. Add user dashboard
3. Implement logout functionality
4. Add password reset flow
5. Enable Google OAuth (requires setup)
6. Add email verification
