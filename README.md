# Stock Vault

<br>

Stock Vault is designed to provide a secure and user-friendly platform for managing and tracking stock portfolios. The project aims to offer a comprehensive tool for users to monitor their investments, access real-time stock data, and organize their financial assets efficiently, catering to both novice and experienced investors.

The Stock Vault system includes features like portfolio tracking, real-time market data integration, and personalized insights to help users make informed investment decisions. It adopts a streamlined approach, enabling users to visualize their financial performance and optimize their strategies. The platform facilitates online access for convenient, self-paced portfolio management, fostering an engaging environment to maximize investment potential and boost confidence in financial planning.

## Features

- Secure authentication and authorization
- Interactive charts and performance metrics
- Multi-portfolio management
- Modern, responsive UI design
- Fast page loads with Next.js optimization
- RESTful API architecture
- Robust PostgreSQL database

## Project Structure

```
StockVault/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   └── ...
├── frontend/
│   ├── app/
│   ├── components/
│   ├── package.json
│   └── ...
└── README.md
```

## Technologies Used

### Backend
- **Framework:** Django
- **Database:** PostgreSQL
- **API:** Django REST Framework
- **Authentication:** JWT tokens

### Frontend
- **Framework:** Next.js 14+ (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **State Management:** React Context API
- **API Client:** Axios
- **Charts:** Chart.js
- **Form Handling:** React Hook Form

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Node.js 18.x or higher
- PostgreSQL database
- npm or yarn package manager

### Quick Start

**1. Clone the repository**

```bash
git clone https://github.com/ghanteyyy/StockVault.git
cd StockVault
```

**2. Backend Setup**

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Configure database
python manage.py makemigrations
python manage.py migrate

# Run the backend server
python manage.py runserver
```

The backend API will be available at `http://127.0.0.1:8000/`

**3. Frontend Setup**

Open a new terminal window:

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Create environment variables file
echo "NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api
NEXT_PUBLIC_APP_URL=http://localhost:3000" > .env.local

# Run the development server
npm run dev
```

The frontend application will be available at `http://localhost:3000`

## Optional Database Configurations

The following configurations are necessary solely for the purpose of generating dummy data for testing.

**1. Populate Stocks**

```bash
python manage.py PopulateStocks
```

**2. Populate Users**

```bash
python manage.py PopulateUsers
```

**3. Populate Companies**

```bash
python manage.py PopulateCompanies
```

**4. Populate Portfolios for respective user**

```bash
python manage.py PopulatePortfolios
```

**5. Populate Testimonials**

```bash
python manage.py PopulateUserTestonomials
```

**6. Populate FAQs**

```bash
python manage.py PopulateFaqs
```

## Development Workflow

### Backend Development

```bash
cd backend
python manage.py runserver
```

Backend server runs on `http://127.0.0.1:8000/`

### Frontend Development

```bash
cd frontend
npm run dev
```

Frontend application runs on `http://localhost:3000`

### Building for Production

**Backend:**
```bash
cd backend
python manage.py collectstatic
# Configure your production settings
```

**Frontend:**
```bash
cd frontend
npm run build
npm run start
```

## API Endpoints

The backend provides RESTful API endpoints for the frontend:

- `POST /api/auth/login/` - User authentication
- `POST /api/auth/register/` - User registration
- `GET /api/portfolios/` - Fetch user portfolios
- `POST /api/portfolios/` - Create new portfolio
- `GET /api/stocks/` - Fetch stock data
- `GET /api/companies/` - Fetch company information
- `GET /api/faqs/` - Fetch FAQs
- `GET /api/testimonials/` - Fetch user testimonials

## Environment Variables

### Backend
Configure your database and Django settings in `backend/settings.py`

### Frontend
Create `.env.local` in the frontend directory:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

## Contributing

We welcome contributions to Stock Vault! Here's how you can help:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Documentation

For more detailed documentation:
- [Backend README](./backend/README.md) - Backend setup and API documentation
- [Frontend README](./frontend/README.md) - Frontend setup and component documentation


**Note:** Make sure both backend and frontend servers are running for full functionality of the application.