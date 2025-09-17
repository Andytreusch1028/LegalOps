# LegalOps Platform - API Documentation

## Overview
The LegalOps Platform provides a comprehensive REST API for business formation, document management, and legal operations. This documentation covers all available endpoints, authentication, and usage examples.

## Table of Contents
1. [Authentication](#authentication)
2. [Base URL](#base-url)
3. [Response Format](#response-format)
4. [Error Handling](#error-handling)
5. [Rate Limiting](#rate-limiting)
6. [API Endpoints](#api-endpoints)
7. [Webhooks](#webhooks)
8. [SDKs](#sdks)

## Authentication

### JWT Token Authentication
All API requests require authentication using JWT tokens.

```bash
# Login to get access token
curl -X POST https://api.legalops.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your_password"
  }'

# Response
{
  "success": true,
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "user_id",
      "email": "user@example.com",
      "firstName": "John",
      "lastName": "Doe"
    }
  }
}
```

### Using Access Tokens
Include the access token in the Authorization header:

```bash
curl -X GET https://api.legalops.com/api/users/profile \
  -H "Authorization: Bearer your_access_token"
```

### Token Refresh
Access tokens expire after 15 minutes. Use the refresh token to get a new access token:

```bash
curl -X POST https://api.legalops.com/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refreshToken": "your_refresh_token"
  }'
```

## Base URL

- **Production**: `https://api.legalops.com`
- **Staging**: `https://staging-api.legalops.com`
- **Development**: `http://localhost:3000`

## Response Format

### Success Response
```json
{
  "success": true,
  "data": {
    // Response data
  },
  "message": "Operation completed successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "reason": "Invalid email format"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Error Handling

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `409` - Conflict
- `422` - Validation Error
- `429` - Rate Limit Exceeded
- `500` - Internal Server Error

### Error Codes
- `VALIDATION_ERROR` - Input validation failed
- `AUTHENTICATION_ERROR` - Authentication failed
- `AUTHORIZATION_ERROR` - Insufficient permissions
- `NOT_FOUND` - Resource not found
- `CONFLICT` - Resource conflict
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `INTERNAL_ERROR` - Server error

## Rate Limiting

- **General API**: 100 requests per minute per IP
- **Authentication**: 5 requests per minute per IP
- **File Upload**: 10 requests per minute per user
- **Business Formation**: 5 requests per minute per user

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248600
```

## API Endpoints

### Authentication Endpoints

#### POST /api/auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password",
  "firstName": "John",
  "lastName": "Doe",
  "phone": "+1234567890"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "user_id",
      "email": "user@example.com",
      "firstName": "John",
      "lastName": "Doe",
      "createdAt": "2024-01-15T10:30:00Z"
    }
  }
}
```

#### POST /api/auth/login
Authenticate user and get access token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

#### POST /api/auth/logout
Logout user and invalidate tokens.

**Headers:**
```
Authorization: Bearer your_access_token
```

#### POST /api/auth/refresh
Refresh access token using refresh token.

**Request Body:**
```json
{
  "refreshToken": "your_refresh_token"
}
```

### User Management Endpoints

#### GET /api/users/profile
Get current user profile.

**Headers:**
```
Authorization: Bearer your_access_token
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "user_id",
    "email": "user@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "phone": "+1234567890",
    "createdAt": "2024-01-15T10:30:00Z",
    "updatedAt": "2024-01-15T10:30:00Z"
  }
}
```

#### PUT /api/users/profile
Update user profile.

**Headers:**
```
Authorization: Bearer your_access_token
```

**Request Body:**
```json
{
  "firstName": "John",
  "lastName": "Doe",
  "phone": "+1234567890"
}
```

#### POST /api/users/change-password
Change user password.

**Headers:**
```
Authorization: Bearer your_access_token
```

**Request Body:**
```json
{
  "currentPassword": "old_password",
  "newPassword": "new_secure_password"
}
```

### Business Formation Endpoints

#### GET /api/business-formation/entities
Get user's business entities.

**Headers:**
```
Authorization: Bearer your_access_token
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 10)
- `status` (optional): Filter by status

**Response:**
```json
{
  "success": true,
  "data": {
    "entities": [
      {
        "id": "entity_id",
        "name": "My Business LLC",
        "type": "LLC",
        "state": "FL",
        "status": "ACTIVE",
        "createdAt": "2024-01-15T10:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 1,
      "pages": 1
    }
  }
}
```

#### POST /api/business-formation/entities
Create a new business entity.

**Headers:**
```
Authorization: Bearer your_access_token
```

**Request Body:**
```json
{
  "name": "My Business LLC",
  "type": "LLC",
  "state": "FL",
  "registeredAgent": {
    "name": "John Doe",
    "address": "123 Main St, Miami, FL 33101",
    "phone": "+1234567890"
  },
  "businessAddress": {
    "street": "456 Business Ave",
    "city": "Miami",
    "state": "FL",
    "zipCode": "33101"
  }
}
```

#### GET /api/business-formation/entities/:id
Get specific business entity details.

**Headers:**
```
Authorization: Bearer your_access_token
```

#### PUT /api/business-formation/entities/:id
Update business entity.

**Headers:**
```
Authorization: Bearer your_access_token
```

#### DELETE /api/business-formation/entities/:id
Delete business entity.

**Headers:**
```
Authorization: Bearer your_access_token
```

### Document Management Endpoints

#### GET /api/documents
Get user's documents.

**Headers:**
```
Authorization: Bearer your_access_token
```

**Query Parameters:**
- `page` (optional): Page number
- `limit` (optional): Items per page
- `type` (optional): Filter by document type
- `entityId` (optional): Filter by business entity

#### POST /api/documents
Upload a new document.

**Headers:**
```
Authorization: Bearer your_access_token
Content-Type: multipart/form-data
```

**Form Data:**
- `file`: Document file
- `name`: Document name
- `type`: Document type
- `entityId` (optional): Associated business entity ID
- `description` (optional): Document description

#### GET /api/documents/:id
Get specific document details.

**Headers:**
```
Authorization: Bearer your_access_token
```

#### PUT /api/documents/:id
Update document metadata.

**Headers:**
```
Authorization: Bearer your_access_token
```

#### DELETE /api/documents/:id
Delete document.

**Headers:**
```
Authorization: Bearer your_access_token
```

#### GET /api/documents/:id/download
Download document file.

**Headers:**
```
Authorization: Bearer your_access_token
```

### AI Assistant Endpoints

#### POST /api/ai-assistant/chat
Send message to AI assistant.

**Headers:**
```
Authorization: Bearer your_access_token
```

**Request Body:**
```json
{
  "message": "How do I form an LLC in Florida?",
  "context": {
    "entityId": "entity_id",
    "documentId": "document_id"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "response": "To form an LLC in Florida, you need to...",
    "disclaimer": "This information is for educational purposes only and does not constitute legal advice.",
    "attorneyReferral": {
      "recommended": true,
      "reason": "Complex legal question requiring professional advice"
    }
  }
}
```

#### GET /api/ai-assistant/conversations
Get user's AI conversations.

**Headers:**
```
Authorization: Bearer your_access_token
```

#### GET /api/ai-assistant/conversations/:id
Get specific conversation.

**Headers:**
```
Authorization: Bearer your_access_token
```

### Analytics Endpoints

#### GET /api/analytics/dashboard
Get analytics dashboard data.

**Headers:**
```
Authorization: Bearer your_access_token
```

**Response:**
```json
{
  "success": true,
  "data": {
    "userStats": {
      "totalEntities": 5,
      "totalDocuments": 23,
      "aiInteractions": 45
    },
    "recentActivity": [
      {
        "type": "ENTITY_CREATED",
        "description": "Created My Business LLC",
        "timestamp": "2024-01-15T10:30:00Z"
      }
    ]
  }
}
```

### Health Check Endpoints

#### GET /health
Basic health check (no authentication required).

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

#### GET /api/health/detailed
Detailed health check (requires authentication).

**Headers:**
```
Authorization: Bearer your_access_token
```

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "services": {
      "database": "healthy",
      "redis": "healthy",
      "storage": "healthy"
    },
    "metrics": {
      "uptime": "72h 15m 30s",
      "memoryUsage": "45%",
      "cpuUsage": "12%"
    }
  }
}
```

## Webhooks

### Webhook Events
- `user.registered` - User registration
- `entity.created` - Business entity created
- `entity.updated` - Business entity updated
- `document.uploaded` - Document uploaded
- `document.processed` - Document processing completed
- `payment.completed` - Payment processed
- `payment.failed` - Payment failed

### Webhook Configuration
```json
{
  "url": "https://your-app.com/webhooks/legalops",
  "events": ["user.registered", "entity.created"],
  "secret": "your_webhook_secret"
}
```

### Webhook Payload Example
```json
{
  "event": "entity.created",
  "data": {
    "id": "entity_id",
    "name": "My Business LLC",
    "type": "LLC",
    "state": "FL"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## SDKs

### JavaScript/Node.js
```bash
npm install @legalops/sdk
```

```javascript
const LegalOps = require('@legalops/sdk');

const client = new LegalOps({
  apiKey: 'your_api_key',
  environment: 'production' // or 'staging'
});

// Create business entity
const entity = await client.businessEntities.create({
  name: 'My Business LLC',
  type: 'LLC',
  state: 'FL'
});
```

### Python
```bash
pip install legalops-sdk
```

```python
from legalops import LegalOpsClient

client = LegalOpsClient(
    api_key='your_api_key',
    environment='production'
)

# Create business entity
entity = client.business_entities.create(
    name='My Business LLC',
    type='LLC',
    state='FL'
)
```

### PHP
```bash
composer require legalops/legalops-php
```

```php
use LegalOps\LegalOpsClient;

$client = new LegalOpsClient([
    'api_key' => 'your_api_key',
    'environment' => 'production'
]);

// Create business entity
$entity = $client->businessEntities->create([
    'name' => 'My Business LLC',
    'type' => 'LLC',
    'state' => 'FL'
]);
```

## Support

- **API Documentation**: https://docs.legalops.com/api
- **Support Email**: api-support@legalops.com
- **Status Page**: https://status.legalops.com
- **GitHub**: https://github.com/legalops/api-examples

---

**Last Updated**: $(date)
**API Version**: v1.0.0
**Environment**: Production

