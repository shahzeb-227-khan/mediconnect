# MediConnect

An Assistant Based full-stack hospital and doctor appointment booking platform built for the Pakistani market. MediConnect connects patients with doctors across multiple hospitals, with dedicated portals for patients, doctors, and administrators.

## Features

### Patient Portal
- **AI Booking Assistant** — conversational Gemini-powered chatbot build using Langgraph multiagent concept, helps patients find the right doctor and book appointments through natural language
- Search doctors by city and specialization across Pakistan
- Browse hospitals and see doctors affiliated with each location
- Book appointments (cash or online payment via Stripe)
- **Token-based queue system** — real-time queue tracker shows your position with no guessing
- View appointment history and leave reviews for completed visits
- Email confirmations for bookings
- Accessible, mobile-first design with smooth animations and keyboard navigation

### Doctor Portal
- Apply to hospitals with fee, schedule, and capacity details (document upload required)
- Track application status (pending / approved / rejected) with real-time updates
- Toggle availability at approved hospitals
- View and manage appointments with token numbers
- Mark appointments complete (only once payment is received)
- Profile management with photo upload via Cloudinary
- Dedicated dark-themed professional interface

### Admin Portal
- **Polished dashboard** with at-a-glance platform stats and action items
- Manage cities, specializations, and hospitals (with image upload)
- Review and approve/reject doctor-hospital affiliation applications
- Oversee all appointments platform-wide (mark cash payments as paid, remove bookings)
- Accessible CRUD operations with confirmation dialogs and keyboard support
- Mobile-responsive admin panel with hamburger navigation

All three portals are strictly role-separated — a user logged into one cannot access the other two until they log out. Each portal has a context-aware footer tailored to its audience.

## Tech Stack

**Backend:** FastAPI, SQLAlchemy, Alembic, PostgreSQL

**Frontend:** React 19, Vite, Tailwind CSS, React Router v7, Axios, lucide-react (icons)

**Integrations:** Stripe (online payments), Cloudinary (image uploads), fastapi-mail (transactional emails), Google Gemini (AI booking assistant)

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (for local PostgreSQL)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

docker-compose up -d      

cp .env.example .env       
alembic upgrade head
uvicorn main:app --reload
```

Backend runs at `http://localhost:8000` (interactive docs at `/docs`).

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env       # set VITE_API_BASE_URL to your backend URL
npm run dev
```

Frontend runs at `http://localhost:5173`.

### Containerized Full-Stack Setup

The root `docker-compose.yml` runs PostgreSQL, the FastAPI backend, and the
Nginx-served React frontend together. Create `backend/.env` from
`backend/.env.example` first, then run:

```bash
docker compose up --build
```

Open the frontend at `http://localhost:8082`. Nginx serves the React SPA and
proxies `/api/` requests to the backend container. The database is available
only inside the Compose network; it is not exposed on a host port.

### Environment Variables

See `backend/.env.example` for the full list of required variables (database, JWT secret, admin credentials, Stripe keys, Cloudinary credentials, mail settings).

## Admin Access

The admin portal has no public link in the UI by design — log in directly at `/admin/login` using the credentials set in `ADMIN_EMAIL` / `ADMIN_PASSWORD`.

## License

Private project — all rights reserved.
