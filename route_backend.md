# CampusBuddy — Frontend Integration Guide

> **Base URL:** `http://localhost:8000` (dev) | `https://your-hf-space.hf.space` (prod)
>
> **Auth:** All protected routes use `httpOnly` cookies (`access_token`, `refresh_token`). The browser sends them automatically with `credentials: 'include'` in fetch calls.

---

## 1. Authentication

### `POST /register` — Create New Student Account
**Access:** Public (no auth required)

**Request Body:**
```json
{
  "name": "Rohan Sharma",
  "email": "rohan.s@campus.edu",
  "password": "securePass123",
  "phone": "+91 9876543210",
  "course": "B.Tech CSE",
  "department": "School of Computer Science",
  "semester": 4,
  "college_id": "24BCE10023"
}
```
> Only `name`, `email`, `password` are required. All other fields are optional.

**Success Response (200):**
```json
{
  "status": "success",
  "message": "Registration successful!",
  "user_id": "a3f5e1b2-..."
}
```

**Error Responses:**
- `409` — Email already registered

---

### `POST /login` — Authenticate User or Admin
**Access:** Public

**Request Body:**
```json
{
  "email": "rohan.s@campus.edu",
  "password": "securePass123"
}
```

**Success Response (200):**
```json
{
  "status": "success",
  "message": "Login successful!",
  "role": "user"
}
```
> On success, `access_token` and `refresh_token` cookies are automatically set by the server. Include `credentials: 'include'` in your fetch config.

**Frontend Fetch Example:**
```js
const res = await fetch('http://localhost:8000/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({ email, password })
});
```

---

### `POST /refresh` — Refresh Access Token
**Access:** Requires valid `refresh_token` cookie

**Request Body:** None

**Success Response:** Re-issues `access_token` cookie automatically.
```json
{ "status": "success", "message": "Token refreshed" }
```

---

### `POST /logout/user` — Logout Student
**Access:** Requires cookies

**Request Body:** None

**Success Response:**
```json
{ "status": "success", "message": "Logout Successful" }
```

---

### `POST /logout/admin` — Logout Admin
**Access:** Requires cookies

**Request Body:** None

**Success Response:**
```json
{ "status": "success", "message": "Logout Successful" }
```

---

## 2. User Profile

### `GET /api/user/profile` — Fetch Logged-In User Context
**Access:** 🔒 Student (cookie auth)
**Used By:** `Navbar`, `ThemeContext`, global user state

**Response (200):**
```json
{
  "id": "a3f5e1b2-...",
  "name": "Rohan Sharma",
  "email": "rohan.s@campus.edu",
  "avatar": "https://url-to-image",
  "course": "B.Tech CSE",
  "semester": 4,
  "dept": "School of Computer Science",
  "collegeId": "24BCE10023",
  "phone": "+91 9876543210"
}
```

**Frontend Fetch Example:**
```js
const res = await fetch('http://localhost:8000/api/user/profile', {
  credentials: 'include'
});
const user = await res.json();
```

---

## 3. Caffenity (Food Module)

### `GET /api/caffenity/canteens` — List All Canteens
**Access:** 🔒 Student

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid-canteen-1",
      "name": "Main Cafe",
      "location": "Block A, Ground Floor",
      "description": "The primary campus food court",
      "is_active": true
    }
  ]
}
```

---

### `GET /api/caffenity/menu` — List Menu Items
**Access:** 🔒 Student
**Query Params:** `?canteen_id=uuid` (optional — filter by canteen)

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid-item-1",
      "canteen_id": "uuid-canteen-1",
      "name": "Paneer Tikka Roll",
      "description": "Spicy paneer wrapped in a warm paratha",
      "category": "North Indian",
      "price": 120.0,
      "prep_time": "10 min",
      "image_url": "https://...",
      "rating": 4.5,
      "calories": 350,
      "is_veg": true,
      "is_special": false,
      "in_stock": true,
      "tags": ["Spicy", "Bestseller"]
    }
  ]
}
```

---

### `POST /api/caffenity/canteens` — Add New Canteen
**Access:** 🔒 Admin Only

**Request Body:**
```json
{
  "name": "Container Cafe",
  "location": "Block C, 1st Floor",
  "description": "Quick bites and beverages",
  "is_active": true
}
```

---

### `POST /api/caffenity/menu` — Add New Menu Item
**Access:** 🔒 Admin Only

**Request Body:**
```json
{
  "canteen_id": "uuid-of-canteen",
  "name": "Cold Coffee",
  "description": "Chilled coffee with ice cream",
  "category": "Beverages",
  "price": 80.0,
  "prep_time": "5 min",
  "image_url": "https://...",
  "calories": 200,
  "is_veg": true,
  "is_special": true,
  "in_stock": true,
  "tags": ["Cold", "Sweet"]
}
```

---

## 4. Shopperz (Marketplace)

### `GET /api/shopperz/retail` — Campus Store Inventory
**Access:** 🔒 Student

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid-retail-1",
      "name": "Pilot G2 Premium Pens",
      "category": "Basic Stationery",
      "price": 450.0,
      "rating": 4.9,
      "reviews": 128,
      "image": "https://...",
      "stock": 14,
      "isDuoSync": true,
      "duoPrice": 400.0
    }
  ]
}
```

---

### `GET /api/shopperz/market` — Student P2P Marketplace
**Access:** 🔒 Student

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid-listing-1",
      "title": "Engineering Drawing Kit",
      "condition": "New-ish",
      "seller": {
        "id": "uuid-seller",
        "name": "Rohan",
        "avatar": "https://...",
        "trustScore": 98
      },
      "price": 850.0,
      "originalPrice": 1200.0,
      "status": "Available",
      "image": "https://..."
    }
  ]
}
```

---

### `POST /api/shopperz/retail` — Add Store Item
**Access:** 🔒 Admin Only

**Request Body:**
```json
{
  "name": "Scientific Calculator",
  "category": "Technical",
  "price": 1200.0,
  "imageUrl": "https://...",
  "stock": 25,
  "isDuoSync": false,
  "duoPrice": null
}
```

---

### `POST /api/shopperz/market` — List Item for Sale
**Access:** 🔒 Student (seller is auto-detected from token)

**Request Body:**
```json
{
  "title": "Used Textbook - Data Structures",
  "condition": "Good",
  "price": 300.0,
  "originalPrice": 550.0,
  "imageUrl": "https://..."
}
```
> The `seller` object is auto-populated from the authenticated user's token. No need to send seller info.

---

## 5. ProblemBox (Issue Tracker)

### `GET /api/problembox/tickets` — Fetch All Tickets
**Access:** 🔒 Student

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "TKT-3092",
      "title": "AC Sparking Noise",
      "location": "Lab 4, Engineering Block",
      "description": "Sparks coming from the main vent.",
      "category": "ac",
      "priority": "Critical",
      "status": "InProgress",
      "reporter": {
        "name": "Rohan Sharma",
        "anonymous": false
      },
      "upvotes": 42,
      "hasResolvedViewed": false,
      "media": ["https://image1.jpg"],
      "timeline": [
        {
          "id": "uuid-step-1",
          "step": "Reported",
          "time": "10:30 AM",
          "active": false,
          "completed": true
        },
        {
          "id": "uuid-step-2",
          "step": "Under Triage",
          "time": "10:45 AM",
          "active": true,
          "completed": false
        }
      ]
    }
  ]
}
```
> When `reporter.anonymous` is `true`, the `reporter.name` will display `"Anonymous Issue"` instead of the real name.

---

### `POST /api/problembox/tickets` — Raise a New Ticket
**Access:** 🔒 Student (reporter auto-linked from token)

**Request Body:**
```json
{
  "title": "Projector Not Working",
  "description": "The ceiling projector in Room 302 shows no signal.",
  "location": "Room 302, IT Block",
  "category": "electronics",
  "priority": "High",
  "anonymous": true,
  "media": ["https://image-of-issue.jpg"]
}
```
> The first timeline step `"Reported"` is auto-created by the backend.

---

## 6. Arena (Events & Teams)

### `GET /api/arena/events` — Fetch All Events
**Access:** 🔒 Student

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid-event-1",
      "title": "CodePulse Hackathon",
      "organizer": "GDSC Tech Club",
      "coverImage": "https://...",
      "date": "2026-04-15",
      "location": "Main Auditorium, Block B",
      "tags": ["Hackathon", "Coding"],
      "status": "Live",
      "mode": "Offline",
      "description": "24-hour hackathon...",
      "fee": 500.0,
      "isPaid": true,
      "prizePot": "₹50,000",
      "timeline": {
        "startsIn": "Now",
        "deadline": "2026-04-14"
      },
      "capacity": {
        "total": 500,
        "filled": 450
      },
      "isFeatured": true
    }
  ]
}
```
> `timeline.startsIn` is computed dynamically by the backend (e.g., `"2d 5h"`, `"Now"`).

---

### `POST /api/arena/events` — Create New Event
**Access:** 🔒 Admin Only

**Request Body:**
```json
{
  "title": "CodePulse Hackathon",
  "organizer": "GDSC Tech Club",
  "description": "24-hour hackathon for all branches.",
  "coverImage": "https://...",
  "mode": "Offline",
  "startTime": "2026-04-15T09:00:00Z",
  "deadline": "2026-04-14T23:59:00Z",
  "isPaid": true,
  "fee": 500.0,
  "maxTeamSize": 4,
  "location": "Main Auditorium, Block B",
  "prizePot": "₹50,000",
  "isFeatured": true,
  "totalCapacity": 500,
  "tags": ["Hackathon", "Coding"]
}
```

---

## 7. UAssist (AI Chat)

### `POST /uassist/chat` — General AI Assistant
**Access:** 🔒 Student

**Request Body:**
```json
{
  "message": "What vegetarian food is available?",
  "session_id": "unique-session-id"
}
```

### `POST /uassist/arena` — Arena-Aware AI Assistant
**Access:** 🔒 Student

**Request Body:**
```json
{
  "message": "Find me a teammate for the hackathon",
  "session_id": "unique-session-id",
  "user_id": "current-user-uuid"
}
```

---

## Quick Reference — All Endpoints

| # | Endpoint | Method | Auth | Role |
|---|----------|--------|------|------|
| 1 | `/register` | POST | ❌ Public | — |
| 2 | `/login` | POST | ❌ Public | — |
| 3 | `/refresh` | POST | 🍪 Cookie | — |
| 4 | `/logout/user` | POST | 🍪 Cookie | — |
| 5 | `/logout/admin` | POST | 🍪 Cookie | **Admin** |
| 6 | `/api/user/profile` | GET | 🔒 | Student |
| 7 | `/api/caffenity/canteens` | GET | 🔒 | Student |
| 8 | `/api/caffenity/menu` | GET | 🔒 | Student |
| 9 | `/api/caffenity/canteens` | POST | 🔒 | **Admin** |
| 10 | `/api/caffenity/menu` | POST | 🔒 | **Admin** |
| 11 | `/api/shopperz/retail` | GET | 🔒 | Student |
| 12 | `/api/shopperz/market` | GET | 🔒 | Student |
| 13 | `/api/shopperz/retail` | POST | 🔒 | **Admin** |
| 14 | `/api/shopperz/market` | POST | 🔒 | Student |
| 15 | `/api/problembox/tickets` | GET | 🔒 | Student |
| 16 | `/api/problembox/tickets` | POST | 🔒 | Student |
| 17 | `/api/arena/events` | GET | 🔒 | Student |
| 18 | `/api/arena/events` | POST | 🔒 | **Admin** |
| 19 | `/uassist/chat` | POST | 🔒 | Student |
| 20 | `/uassist/arena` | POST | 🔒 | Student |

---

## Frontend Fetch Config Reminder

All authenticated requests **must** include `credentials: 'include'`:
```js
const fetchOptions = {
  method: 'GET', // or 'POST'
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include'  // ← THIS IS CRITICAL for cookie auth
};
```
