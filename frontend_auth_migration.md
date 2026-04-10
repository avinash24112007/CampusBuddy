# 🔧 Frontend Auth Migration Guide — BREAKING CHANGE

> **From:** Cookie-based authentication
> **To:** Bearer token authentication
> **Reason:** HF Spaces reverse proxy strips `Set-Cookie` headers on cross-domain responses. Cookies between `vercel.app` → `hf.space` are blocked.

---

## What Changed on the Backend

1. **`POST /login`** now returns `access_token` and `refresh_token` directly in the JSON response body.
2. **All protected routes** now read the token from the `Authorization` header first, cookies second.

---

## What the Frontend Must Change

### 1. Login Handler — Store Tokens from Response Body

**Before:**
```js
const res = await fetch(`${API_BASE}/login`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({ email, password })
});
const data = await res.json();
// ❌ Relied on Set-Cookie headers (no longer works cross-domain)
```

**After:**
```js
const res = await fetch(`${API_BASE}/login`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
});
const data = await res.json();

if (data.status === 'success') {
  // ✅ Store tokens from JSON body
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
  localStorage.setItem('role', data.role);
}
```

---

### 2. Create a Shared Fetch Wrapper — Inject Bearer Header Everywhere

Create a utility function that **every API call** routes through:

```js
// utils/api.js
const API_BASE = 'https://your-hf-space.hf.space';

export async function apiFetch(endpoint, options = {}) {
  const token = localStorage.getItem('access_token');

  const headers = {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
    ...options.headers
  };

  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers
  });

  // Optional: auto-handle 401 by redirecting to login
  if (res.status === 401) {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
    return;
  }

  return res.json();
}
```

**Usage across all components:**
```js
import { apiFetch } from '../utils/api';

// GET user profile
const profile = await apiFetch('/api/user/profile');

// GET canteens
const canteens = await apiFetch('/api/caffenity/canteens');

// POST a new ticket
const ticket = await apiFetch('/api/problembox/tickets', {
  method: 'POST',
  body: JSON.stringify({ title: '...', description: '...' })
});
```

---

### 3. Update Every Existing Fetch Call

Search your entire frontend codebase and replace raw `fetch()` calls to protected endpoints:

**Before (remove these):**
```js
credentials: 'include'  // ← DELETE THIS everywhere
```

**After (add this header):**
```js
headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
```

Or better yet, just switch every call to use `apiFetch()` from Step 2.

---

### 4. Registration — No Auth Needed

`POST /register` is public. No token required:
```js
const res = await fetch(`${API_BASE}/register`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'Rohan Sharma',
    email: 'rohan@campus.edu',
    password: 'secure123',
    phone: '+91 9876543210',
    course: 'B.Tech CSE',
    department: 'School of Computer Science',
    semester: 4,
    college_id: '24BCE10023'
  })
});
```

---

### 5. Logout — Clear Local Storage

```js
function logout() {
  // Optional: tell the backend to invalidate the refresh token
  apiFetch('/logout/user', { method: 'POST' });

  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('role');
  window.location.href = '/login';
}
```

---

### 6. Auth State Check (Route Guards)

Use this to protect frontend routes:
```js
export function isLoggedIn() {
  return !!localStorage.getItem('access_token');
}

export function getUserRole() {
  return localStorage.getItem('role'); // 'user' or 'admin'
}
```

---

## Quick Checklist

- [ ] Login handler stores `access_token`, `refresh_token`, `role` from response body
- [ ] Created `apiFetch()` wrapper that injects `Authorization: Bearer` header
- [ ] Replaced all `fetch()` calls to protected endpoints with `apiFetch()`
- [ ] Removed all `credentials: 'include'` from fetch configs
- [ ] Logout clears `localStorage` tokens
- [ ] Route guards check `localStorage` for auth state

---

## Login Response Shape (for reference)

```json
{
  "status": "success",
  "message": "Login successful!",
  "role": "user",
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```
