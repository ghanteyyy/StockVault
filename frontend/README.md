# Stock Vault - Frontend

<br>

Stock Vault is designed to provide a secure and user-friendly platform for managing and tracking stock portfolios. The project aims to offer a comprehensive tool for users to monitor their investments, access real-time stock data, and organize their financial assets efficiently, catering to both novice and experienced investors.

The Stock Vault system includes features like portfolio tracking, real-time market data integration, and personalized insights to help users make informed investment decisions. It adopts a streamlined approach, enabling users to visualize their financial performance and optimize their strategies. The platform facilitates online access for convenient, self-paced portfolio management, fostering an engaging environment to maximize investment potential and boost confidence in financial planning.

## Features

- Secure authentication and authorization
- Interactive charts and performance metrics
- Multi-portfolio management
- Modern, responsive UI design
- Fast page loads with Next.js optimization

## Getting Started

If you are new to the project, here are some initial steps to get started:

### Prerequisites

- Node.js 18.x or higher
- npm or yarn package manager
- Backend API running (see [backend README](../backend/README.md))

### Installation

**1. Clone the project**

```bash
git clone https://github.com/ghanteyyy/StockVault.git
cd StockVault/frontend
```

**2. Install Dependencies**

```bash
npm install
# or
yarn install
```

**3. Configure Environment Variables**

Create a `.env.local` file in the root directory:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

**4. Run the development server**

```bash
npm run dev
# or
yarn dev
```

**5. Open the application in your web browser**

```
http://localhost:3000
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

## Building for Production

**1. Build the application**

```bash
npm run build
```

**2. Start the production server**

```bash
npm run start
```

The application will be available at `http://localhost:3000`

## Technologies Used

- **Framework:** Next.js 14+ (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **State Management:** React Context API
- **API Client:** Axios
- **Charts:** Chart.js
- **Form Handling:** React Hook Form
- **Authentication:** JWT tokens

## Key Dependencies

```json
{
  "next": "^14.0.0",
  "react": "^18.0.0",
  "typescript": "^5.0.0",
  "tailwindcss": "^3.0.0",
  "axios": "^1.6.0",
  "recharts": "^2.10.0"
}
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `http://127.0.0.1:8000/api` |
| `NEXT_PUBLIC_APP_URL` | Frontend application URL | `http://localhost:3000` |

## API Integration

The frontend communicates with the Django backend through RESTful APIs. Make sure the backend server is running before starting the frontend application.

Example API endpoints:
- `GET /api/portfolios/` - Fetch user portfolios
- `GET /api/stocks/` - Fetch stock data
- `POST /api/auth/login/` - User authentication

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
