# LegalOps - Legal Operations Management System

A comprehensive legal operations management system built with Node.js, Docker, PostgreSQL, Redis, and Elasticsearch.

## 🚀 Features

- **Client Management**: Manage clients, matters, and case files
- **Document Management**: Secure document storage and retrieval
- **Time Tracking**: Billable hours and time entry management
- **User Management**: Role-based access control (Admin, Lawyer, Paralegal, User)
- **Search**: Full-text search capabilities with Elasticsearch
- **Security**: JWT authentication, rate limiting, and security headers
- **Scalability**: Docker containerized microservices architecture

## 🏗️ Architecture

- **Frontend**: Node.js/Express API server
- **Database**: PostgreSQL with comprehensive legal operations schema
- **Cache**: Redis for session management and caching
- **Search**: Elasticsearch for document and case search
- **Proxy**: Nginx reverse proxy with rate limiting and security headers
- **Containerization**: Docker and Docker Compose for easy deployment

## 📋 Prerequisites

- Docker and Docker Compose
- Git (for version control)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/LegalOps.git
cd LegalOps
```

### 2. Start the Application

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps
```

### 3. Access the Application

- **Main Application**: http://localhost
- **Direct API**: http://localhost:3000
- **Health Check**: http://localhost/health
- **Database**: localhost:5432 (PostgreSQL)
- **Cache**: localhost:6379 (Redis)
- **Search**: localhost:9200 (Elasticsearch)

## 🔧 Development

### Available Scripts

```bash
# Start development environment
docker-compose up -d

# View logs
docker-compose logs -f

# Rebuild and restart
docker-compose up -d --build

# Stop all services
docker-compose down

# Access database
docker-compose exec postgres psql -U legalops -d legalops_db
```

### Project Structure

```
LegalOps/
├── server.js              # Main application server
├── package.json           # Node.js dependencies
├── Dockerfile            # Application container definition
├── docker-compose.yml    # Multi-service orchestration
├── nginx.conf            # Nginx configuration
├── .gitignore           # Git ignore rules
├── init-scripts/        # Database initialization
│   └── 01-init-db.sql   # Database schema
├── uploads/             # File upload directory
├── logs/                # Application logs
└── README.md           # This file
```

## 🗄️ Database Schema

The system includes the following main entities:

- **Users**: Authentication and user management
- **Clients**: Client information and contact details
- **Matters**: Legal cases and matters
- **Documents**: File storage and metadata
- **Time Entries**: Billable hours tracking

## 🔐 Security Features

- JWT-based authentication
- Password hashing with bcrypt
- Rate limiting on API endpoints
- Security headers via Helmet.js
- CORS protection
- Input validation and sanitization

## 🌐 API Endpoints

- `GET /health` - Health check
- `GET /api/status` - API status
- `POST /api/auth/login` - User authentication
- `GET /api/clients` - List clients
- `POST /api/clients` - Create client
- `GET /api/matters` - List matters
- `POST /api/matters` - Create matter

## 🐳 Docker Services

| Service | Port | Description |
|---------|------|-------------|
| legalops-app | 3000 | Main application |
| nginx | 80, 443 | Reverse proxy |
| postgres | 5432 | Database |
| redis | 6379 | Cache |
| elasticsearch | 9200 | Search engine |

## 📝 Environment Variables

Copy `env.example` to `.env` and configure:

```bash
cp env.example .env
```

Key variables:
- `NODE_ENV`: Environment (development/production)
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `JWT_SECRET`: JWT signing secret
- `ALLOWED_ORIGINS`: CORS allowed origins

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -m 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the Docker logs: `docker-compose logs -f`

## 🗺️ Roadmap

- [ ] Replace SQLite with PostgreSQL (completed)
- [ ] Add user authentication
- [ ] Implement document management
- [ ] Add time tracking features
- [ ] Create admin dashboard
- [ ] Add reporting capabilities
- [ ] Implement email notifications
- [ ] Add mobile app support
