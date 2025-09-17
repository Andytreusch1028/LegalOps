# LegalOps Platform - Testing Guide

## Overview
This guide provides comprehensive testing procedures for the LegalOps platform, covering unit tests, integration tests, performance tests, and security tests.

## Table of Contents
1. [Testing Strategy](#testing-strategy)
2. [Test Environment Setup](#test-environment-setup)
3. [Unit Testing](#unit-testing)
4. [Integration Testing](#integration-testing)
5. [Contract Testing](#contract-testing)
6. [Performance Testing](#performance-testing)
7. [Security Testing](#security-testing)
8. [End-to-End Testing](#end-to-end-testing)
9. [Test Automation](#test-automation)
10. [Test Data Management](#test-data-management)

## Testing Strategy

### Testing Pyramid
```
    /\
   /  \
  /E2E \     (10% - Critical user journeys)
 /______\
/        \
/Integration\ (20% - API and service integration)
/____________\
/              \
/   Unit Tests   \ (70% - Individual functions and components)
/________________\
```

### Test Types
- **Unit Tests**: Individual functions and components
- **Integration Tests**: API endpoints and service integration
- **Contract Tests**: API contract validation
- **Performance Tests**: Load and stress testing
- **Security Tests**: Vulnerability and penetration testing
- **End-to-End Tests**: Complete user workflows

## Test Environment Setup

### Prerequisites
```bash
# Install Node.js 18.17.0+
node --version

# Install dependencies
cd backend
npm install

# Install test dependencies
npm install --save-dev jest supertest @types/jest
```

### Environment Configuration
```bash
# Create test environment file
cp .env.test.example .env.test

# Set test environment variables
export NODE_ENV=test
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=legalops_test
export DB_USER=postgres
export DB_PASSWORD=postgres
export REDIS_HOST=localhost
export REDIS_PORT=6379
```

### Database Setup
```bash
# Create test database
createdb legalops_test

# Run migrations
npm run migrate:test

# Seed test data
npm run seed:test
```

## Unit Testing

### Test Structure
```
backend/tests/
├── unit/
│   ├── services/
│   ├── controllers/
│   ├── middleware/
│   └── utils/
├── integration/
├── contracts/
└── helpers/
```

### Example Unit Test
```javascript
// tests/unit/services/authService.test.ts
import { AuthService } from '../../src/services/authService';
import { User } from '../../src/models/User';

describe('AuthService', () => {
  let authService: AuthService;

  beforeEach(() => {
    authService = new AuthService();
  });

  describe('hashPassword', () => {
    it('should hash password correctly', async () => {
      const password = 'testPassword123';
      const hashedPassword = await authService.hashPassword(password);
      
      expect(hashedPassword).toBeDefined();
      expect(hashedPassword).not.toBe(password);
      expect(hashedPassword.length).toBeGreaterThan(50);
    });

    it('should generate different hashes for same password', async () => {
      const password = 'testPassword123';
      const hash1 = await authService.hashPassword(password);
      const hash2 = await authService.hashPassword(password);
      
      expect(hash1).not.toBe(hash2);
    });
  });

  describe('verifyPassword', () => {
    it('should verify correct password', async () => {
      const password = 'testPassword123';
      const hashedPassword = await authService.hashPassword(password);
      
      const isValid = await authService.verifyPassword(password, hashedPassword);
      expect(isValid).toBe(true);
    });

    it('should reject incorrect password', async () => {
      const password = 'testPassword123';
      const wrongPassword = 'wrongPassword';
      const hashedPassword = await authService.hashPassword(password);
      
      const isValid = await authService.verifyPassword(wrongPassword, hashedPassword);
      expect(isValid).toBe(false);
    });
  });
});
```

### Running Unit Tests
```bash
# Run all unit tests
npm run test:unit

# Run specific test file
npm run test:unit -- --testPathPattern=authService

# Run with coverage
npm run test:unit -- --coverage

# Run in watch mode
npm run test:unit -- --watch
```

## Integration Testing

### API Integration Tests
```javascript
// tests/integration/auth.integration.test.ts
import request from 'supertest';
import { app } from '../../src/app';
import { db } from '../../src/config/database';

describe('Auth Integration Tests', () => {
  beforeEach(async () => {
    // Clean database
    await db.query('DELETE FROM users');
  });

  afterAll(async () => {
    await db.end();
  });

  describe('POST /api/auth/register', () => {
    it('should register a new user', async () => {
      const userData = {
        email: 'test@example.com',
        password: 'testPassword123',
        firstName: 'John',
        lastName: 'Doe'
      };

      const response = await request(app)
        .post('/api/auth/register')
        .send(userData)
        .expect(201);

      expect(response.body.success).toBe(true);
      expect(response.body.data.user.email).toBe(userData.email);
      expect(response.body.data.user.password).toBeUndefined();
    });

    it('should reject duplicate email', async () => {
      const userData = {
        email: 'test@example.com',
        password: 'testPassword123',
        firstName: 'John',
        lastName: 'Doe'
      };

      // Register first user
      await request(app)
        .post('/api/auth/register')
        .send(userData)
        .expect(201);

      // Try to register with same email
      const response = await request(app)
        .post('/api/auth/register')
        .send(userData)
        .expect(409);

      expect(response.body.success).toBe(false);
      expect(response.body.error.code).toBe('CONFLICT');
    });
  });

  describe('POST /api/auth/login', () => {
    beforeEach(async () => {
      // Create test user
      const userData = {
        email: 'test@example.com',
        password: 'testPassword123',
        firstName: 'John',
        lastName: 'Doe'
      };

      await request(app)
        .post('/api/auth/register')
        .send(userData);
    });

    it('should login with valid credentials', async () => {
      const loginData = {
        email: 'test@example.com',
        password: 'testPassword123'
      };

      const response = await request(app)
        .post('/api/auth/login')
        .send(loginData)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.accessToken).toBeDefined();
      expect(response.body.data.refreshToken).toBeDefined();
      expect(response.body.data.user.email).toBe(loginData.email);
    });

    it('should reject invalid credentials', async () => {
      const loginData = {
        email: 'test@example.com',
        password: 'wrongPassword'
      };

      const response = await request(app)
        .post('/api/auth/login')
        .send(loginData)
        .expect(401);

      expect(response.body.success).toBe(false);
      expect(response.body.error.code).toBe('AUTHENTICATION_ERROR');
    });
  });
});
```

### Database Integration Tests
```javascript
// tests/integration/database.integration.test.ts
import { db } from '../../src/config/database';
import { UserService } from '../../src/services/userService';

describe('Database Integration Tests', () => {
  let userService: UserService;

  beforeEach(() => {
    userService = new UserService();
  });

  afterEach(async () => {
    await db.query('DELETE FROM users');
  });

  afterAll(async () => {
    await db.end();
  });

  describe('User CRUD Operations', () => {
    it('should create, read, update, and delete user', async () => {
      // Create
      const userData = {
        email: 'test@example.com',
        password: 'testPassword123',
        firstName: 'John',
        lastName: 'Doe'
      };

      const createdUser = await userService.createUser(userData);
      expect(createdUser.id).toBeDefined();
      expect(createdUser.email).toBe(userData.email);

      // Read
      const retrievedUser = await userService.getUserById(createdUser.id);
      expect(retrievedUser.email).toBe(userData.email);

      // Update
      const updateData = { firstName: 'Jane' };
      const updatedUser = await userService.updateUser(createdUser.id, updateData);
      expect(updatedUser.firstName).toBe('Jane');

      // Delete
      await userService.deleteUser(createdUser.id);
      const deletedUser = await userService.getUserById(createdUser.id);
      expect(deletedUser).toBeNull();
    });
  });
});
```

### Running Integration Tests
```bash
# Run all integration tests
npm run test:integration

# Run specific integration test
npm run test:integration -- --testPathPattern=auth

# Run with database
npm run test:integration -- --detectOpenHandles
```

## Contract Testing

### API Contract Tests
```javascript
// tests/contracts/auth.contract.test.ts
import request from 'supertest';
import { app } from '../../src/app';

describe('Auth API Contract Tests', () => {
  describe('POST /api/auth/register', () => {
    it('should match expected contract', async () => {
      const userData = {
        email: 'test@example.com',
        password: 'testPassword123',
        firstName: 'John',
        lastName: 'Doe'
      };

      const response = await request(app)
        .post('/api/auth/register')
        .send(userData)
        .expect(201);

      // Validate response structure
      expect(response.body).toHaveProperty('success', true);
      expect(response.body).toHaveProperty('data');
      expect(response.body.data).toHaveProperty('user');
      expect(response.body.data.user).toHaveProperty('id');
      expect(response.body.data.user).toHaveProperty('email');
      expect(response.body.data.user).toHaveProperty('firstName');
      expect(response.body.data.user).toHaveProperty('lastName');
      expect(response.body.data.user).toHaveProperty('createdAt');
      expect(response.body.data.user).not.toHaveProperty('password');
    });
  });

  describe('POST /api/auth/login', () => {
    it('should match expected contract', async () => {
      const loginData = {
        email: 'test@example.com',
        password: 'testPassword123'
      };

      const response = await request(app)
        .post('/api/auth/login')
        .send(loginData)
        .expect(200);

      // Validate response structure
      expect(response.body).toHaveProperty('success', true);
      expect(response.body).toHaveProperty('data');
      expect(response.body.data).toHaveProperty('accessToken');
      expect(response.body.data).toHaveProperty('refreshToken');
      expect(response.body.data).toHaveProperty('user');
      expect(response.body.data.user).toHaveProperty('id');
      expect(response.body.data.user).toHaveProperty('email');
    });
  });
});
```

## Performance Testing

### Load Testing with Artillery
```yaml
# tests/performance/load-test.yml
config:
  target: 'http://localhost:3000'
  phases:
    - duration: 60
      arrivalRate: 10
    - duration: 120
      arrivalRate: 20
    - duration: 60
      arrivalRate: 10
  defaults:
    headers:
      Content-Type: 'application/json'

scenarios:
  - name: "User Registration"
    weight: 30
    flow:
      - post:
          url: "/api/auth/register"
          json:
            email: "user{{ $randomInt(1, 10000) }}@example.com"
            password: "testPassword123"
            firstName: "John"
            lastName: "Doe"

  - name: "User Login"
    weight: 40
    flow:
      - post:
          url: "/api/auth/login"
          json:
            email: "test@example.com"
            password: "testPassword123"

  - name: "Get User Profile"
    weight: 30
    flow:
      - post:
          url: "/api/auth/login"
          json:
            email: "test@example.com"
            password: "testPassword123"
      - get:
          url: "/api/users/profile"
          headers:
            Authorization: "Bearer {{ accessToken }}"
```

### Performance Test Script
```javascript
// tests/performance/performance.test.js
const { performance } = require('perf_hooks');
const request = require('supertest');
const { app } = require('../../src/app');

describe('Performance Tests', () => {
  describe('API Response Times', () => {
    it('should respond to health check within 100ms', async () => {
      const start = performance.now();
      
      await request(app)
        .get('/health')
        .expect(200);
      
      const end = performance.now();
      const responseTime = end - start;
      
      expect(responseTime).toBeLessThan(100);
    });

    it('should handle concurrent requests efficiently', async () => {
      const concurrentRequests = 50;
      const promises = [];
      
      const start = performance.now();
      
      for (let i = 0; i < concurrentRequests; i++) {
        promises.push(
          request(app)
            .get('/health')
            .expect(200)
        );
      }
      
      await Promise.all(promises);
      
      const end = performance.now();
      const totalTime = end - start;
      const averageTime = totalTime / concurrentRequests;
      
      expect(averageTime).toBeLessThan(200);
    });
  });
});
```

### Running Performance Tests
```bash
# Install Artillery
npm install -g artillery

# Run load tests
artillery run tests/performance/load-test.yml

# Run performance tests
npm run test:performance

# Run stress tests
npm run test:stress
```

## Security Testing

### Security Test Suite
```javascript
// tests/security/security.test.ts
import request from 'supertest';
import { app } from '../../src/app';

describe('Security Tests', () => {
  describe('Authentication Security', () => {
    it('should reject requests without authentication', async () => {
      await request(app)
        .get('/api/users/profile')
        .expect(401);
    });

    it('should reject invalid JWT tokens', async () => {
      await request(app)
        .get('/api/users/profile')
        .set('Authorization', 'Bearer invalid-token')
        .expect(401);
    });

    it('should reject expired JWT tokens', async () => {
      const expiredToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...';
      
      await request(app)
        .get('/api/users/profile')
        .set('Authorization', `Bearer ${expiredToken}`)
        .expect(401);
    });
  });

  describe('Input Validation', () => {
    it('should reject SQL injection attempts', async () => {
      const maliciousInput = "'; DROP TABLE users; --";
      
      const response = await request(app)
        .post('/api/auth/register')
        .send({
          email: maliciousInput,
          password: 'testPassword123',
          firstName: 'John',
          lastName: 'Doe'
        })
        .expect(400);
      
      expect(response.body.success).toBe(false);
    });

    it('should reject XSS attempts', async () => {
      const xssPayload = '<script>alert("XSS")</script>';
      
      const response = await request(app)
        .post('/api/auth/register')
        .send({
          email: 'test@example.com',
          password: 'testPassword123',
          firstName: xssPayload,
          lastName: 'Doe'
        })
        .expect(400);
      
      expect(response.body.success).toBe(false);
    });
  });

  describe('Rate Limiting', () => {
    it('should enforce rate limits', async () => {
      const requests = [];
      
      // Make 10 requests quickly
      for (let i = 0; i < 10; i++) {
        requests.push(
          request(app)
            .post('/api/auth/login')
            .send({
              email: 'test@example.com',
              password: 'wrongPassword'
            })
        );
      }
      
      const responses = await Promise.all(requests);
      const rateLimitedResponses = responses.filter(r => r.status === 429);
      
      expect(rateLimitedResponses.length).toBeGreaterThan(0);
    });
  });
});
```

### Running Security Tests
```bash
# Run security tests
npm run test:security

# Run OWASP ZAP scan
npm run test:security:zap

# Run dependency audit
npm audit

# Run security linting
npm run lint:security
```

## End-to-End Testing

### E2E Test Setup
```javascript
// tests/e2e/user-journey.test.ts
import { test, expect } from '@playwright/test';

test.describe('User Journey Tests', () => {
  test('Complete user registration and business formation flow', async ({ page }) => {
    // Navigate to registration page
    await page.goto('https://app.legalops.com/register');
    
    // Fill registration form
    await page.fill('[data-testid="email"]', 'test@example.com');
    await page.fill('[data-testid="password"]', 'testPassword123');
    await page.fill('[data-testid="firstName"]', 'John');
    await page.fill('[data-testid="lastName"]', 'Doe');
    
    // Submit registration
    await page.click('[data-testid="register-button"]');
    
    // Verify successful registration
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
    
    // Navigate to business formation
    await page.click('[data-testid="create-business-button"]');
    
    // Fill business formation form
    await page.fill('[data-testid="business-name"]', 'My Business LLC');
    await page.selectOption('[data-testid="business-type"]', 'LLC');
    await page.selectOption('[data-testid="business-state"]', 'FL');
    
    // Submit business formation
    await page.click('[data-testid="submit-business-button"]');
    
    // Verify business creation
    await expect(page.locator('[data-testid="business-created"]')).toBeVisible();
  });
});
```

## Test Automation

### GitHub Actions Workflow
```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: legalops_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:6.2
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18.17.0'
        cache: 'npm'
        cache-dependency-path: backend/package-lock.json
    
    - name: Install dependencies
      run: |
        cd backend
        npm ci
    
    - name: Run linting
      run: |
        cd backend
        npm run lint
    
    - name: Run unit tests
      run: |
        cd backend
        npm run test:unit -- --coverage
    
    - name: Run integration tests
      run: |
        cd backend
        npm run test:integration -- --detectOpenHandles
    
    - name: Run security tests
      run: |
        cd backend
        npm run test:security
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: backend/coverage/lcov.info
```

## Test Data Management

### Test Data Factory
```javascript
// tests/helpers/testDataFactory.ts
export class TestDataFactory {
  static createUser(overrides = {}) {
    return {
      email: `test${Date.now()}@example.com`,
      password: 'testPassword123',
      firstName: 'John',
      lastName: 'Doe',
      phone: '+1234567890',
      ...overrides
    };
  }

  static createBusinessEntity(overrides = {}) {
    return {
      name: `Test Business ${Date.now()}`,
      type: 'LLC',
      state: 'FL',
      registeredAgent: {
        name: 'John Doe',
        address: '123 Main St, Miami, FL 33101',
        phone: '+1234567890'
      },
      businessAddress: {
        street: '456 Business Ave',
        city: 'Miami',
        state: 'FL',
        zipCode: '33101'
      },
      ...overrides
    };
  }

  static createDocument(overrides = {}) {
    return {
      name: `Test Document ${Date.now()}`,
      type: 'CONTRACT',
      description: 'Test document description',
      ...overrides
    };
  }
}
```

### Test Database Seeding
```javascript
// tests/helpers/seedTestData.ts
import { db } from '../../src/config/database';
import { TestDataFactory } from './testDataFactory';

export class TestDataSeeder {
  static async seedUsers(count = 10) {
    const users = [];
    for (let i = 0; i < count; i++) {
      const userData = TestDataFactory.createUser();
      const result = await db.query(
        'INSERT INTO users (email, password, first_name, last_name, phone) VALUES ($1, $2, $3, $4, $5) RETURNING *',
        [userData.email, userData.password, userData.firstName, userData.lastName, userData.phone]
      );
      users.push(result.rows[0]);
    }
    return users;
  }

  static async seedBusinessEntities(userId, count = 5) {
    const entities = [];
    for (let i = 0; i < count; i++) {
      const entityData = TestDataFactory.createBusinessEntity();
      const result = await db.query(
        'INSERT INTO business_entities (name, type, state, user_id) VALUES ($1, $2, $3, $4) RETURNING *',
        [entityData.name, entityData.type, entityData.state, userId]
      );
      entities.push(result.rows[0]);
    }
    return entities;
  }

  static async cleanDatabase() {
    await db.query('DELETE FROM documents');
    await db.query('DELETE FROM business_entities');
    await db.query('DELETE FROM users');
  }
}
```

## Running All Tests

### Test Commands
```bash
# Run all tests
npm test

# Run specific test suites
npm run test:unit
npm run test:integration
npm run test:contract
npm run test:performance
npm run test:security
npm run test:e2e

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm run test:watch

# Run tests with debugging
npm run test:debug

# Run tests with open handles detection
npm run test:integration -- --detectOpenHandles
```

### Test Coverage
```bash
# Generate coverage report
npm run test:coverage

# View coverage report
open coverage/lcov-report/index.html

# Check coverage thresholds
npm run test:coverage -- --coverageThreshold='{"global":{"branches":80,"functions":80,"lines":80,"statements":80}}'
```

## Best Practices

### Test Organization
- Group related tests in describe blocks
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)
- Keep tests independent and isolated
- Use meaningful assertions

### Test Data
- Use factories for test data creation
- Clean up test data after each test
- Use realistic test data
- Avoid hardcoded values
- Use unique identifiers for test data

### Performance
- Mock external dependencies
- Use database transactions for isolation
- Clean up resources properly
- Use appropriate timeouts
- Monitor test execution time

### Security
- Test authentication and authorization
- Validate input sanitization
- Test rate limiting
- Check for common vulnerabilities
- Use security testing tools

---

**Last Updated**: $(date)
**Version**: 1.0.0
**Environment**: All

