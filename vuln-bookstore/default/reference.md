# ⚠️ VulnBookStore — Intentionally Vulnerable Application

> ## 🚨 WARNING: DO NOT USE IN PRODUCTION 🚨
>
> This application is **INTENTIONALLY VULNERABLE** and is designed **SOLELY for educational purposes**.
> It contains deliberate security vulnerabilities to demonstrate GitHub Advanced Security (GHAS) scanning capabilities.
>
> **DO NOT:**
> - Deploy this application to any production or staging environment
> - Use any of the security patterns shown here in real applications
> - Store real user data in this application
>
> **This repository is safe to make public** — it contains no real secrets or sensitive data.
> All "secrets" are fake, hardcoded demonstration values.

---

## 📖 About VulnBookStore

VulnBookStore is a realistic-looking REST API for managing a bookstore (books, users, and orders). It is intentionally built with a variety of security vulnerabilities at different severity levels and subtlety, making it an ideal target for demonstrating **GitHub Advanced Security (GHAS)** tooling:

| GHAS Feature | What It Detects Here |
|---|---|
| **CodeQL** | SQL injection, command injection, XSS, path traversal, insecure deserialization, weak crypto |
| **Secret Scanning** | Hardcoded JWT secrets, API keys, database passwords, encryption keys |
| **Dependency Review** | Known CVEs in `commons-collections 3.2.1`, `log4j-core 2.14.1` |

---

## 🛠️ Tech Stack

- **Java 17**
- **Spring Boot 3.1.x**
- **Maven**
- **H2 In-Memory Database**
- **Spring Security**
- **JUnit 5 + Mockito**

---

## 🐛 Vulnerability Categories

The following categories of vulnerabilities are intentionally embedded in this codebase. Exact locations are not listed here — use GHAS to find them!

### Injection Vulnerabilities
- SQL Injection (obvious)
- Command Injection (subtle — looks like a legitimate feature)

### Broken Authentication & Session Management
- Plaintext password storage
- Weak password reset token generation
- Hardcoded credentials
- JWT with hardcoded secret and no expiration validation

### Sensitive Data Exposure
- Passwords returned in API responses
- Hardcoded secrets in source code
- Hardcoded secrets in configuration files

### Broken Access Control
- Missing authorization checks
- Header-based "authentication" bypass
- Overly permissive security configuration

### Security Misconfiguration
- CSRF disabled
- H2 console exposed
- Debug/verbose SQL logging enabled
- Overly permissive CORS/security rules

### Cryptographic Failures
- MD5 used for password hashing
- DES with ECB mode for encryption
- Hardcoded encryption keys
- Weak random number generation (`java.util.Random` instead of `SecureRandom`)

### Insecure Deserialization
- Raw `ObjectInputStream` without class filtering

### Path Traversal
- File read/write operations without path sanitization

### Cross-Site Scripting (XSS)
- Unescaped user input rendered as HTML

### Vulnerable Dependencies
- `commons-collections:3.2.1` — known deserialization gadget chains (CVE-2015-6420, CVE-2015-7501)
- `log4j-core:2.14.1` — Log4Shell (CVE-2021-44228)

---

## 🚀 Setup & Running

### Prerequisites
- Java 17+
- Maven 3.8+

### Build & Run

```bash
# Clone the repository
git clone https://github.com/your-org/vulnbookstore.git
cd vulnbookstore

# Build the project
mvn clean package -DskipTests

# Run the application
mvn spring-boot:run
```

The application will start on `http://localhost:8080`.

### H2 Console

The H2 database console is available at: `http://localhost:8080/h2-console`
- JDBC URL: `jdbc:h2:mem:vulnbookstore`
- Username: `sa`
- Password: `admin123`

### Running Tests

```bash
mvn test
```

---

## 📡 API Endpoints

### Books
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/books` | List all books |
| GET | `/api/books/{id}` | Get book by ID |
| POST | `/api/books` | Create a book |
| PUT | `/api/books/{id}` | Update a book |
| DELETE | `/api/books/{id}` | Delete a book |
| GET | `/api/books/search?q={query}` | Search books (⚠️ vulnerable) |
| GET | `/api/books/{id}/render-description` | Render book description as HTML (⚠️ vulnerable) |
| GET | `/api/books/export?format={format}` | Export book data (⚠️ vulnerable) |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/users/register` | Register a new user |
| POST | `/api/users/login` | Login |
| GET | `/api/users/{id}` | Get user (⚠️ exposes password) |
| GET | `/api/admin/users` | List all users (⚠️ broken access control) |

### Orders
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/orders` | List all orders |
| POST | `/api/orders` | Create an order |
| GET | `/api/orders/{id}` | Get order by ID |

---

## 🔍 Using with GitHub Advanced Security

### Enabling GHAS on Your Fork

1. Fork this repository
2. Go to **Settings → Security → Code security and analysis**
3. Enable **CodeQL analysis**, **Secret scanning**, and **Dependency review**
4. Push a commit or trigger the included CI workflow

### Expected Findings

After enabling GHAS, you should see alerts in the **Security** tab for:
- Multiple CodeQL alerts across different CWE categories
- Secret scanning alerts for hardcoded credentials
- Dependabot alerts for vulnerable dependencies

---

## 📚 Educational Resources

- [GitHub Advanced Security Documentation](https://docs.github.com/en/code-security)
- [CodeQL Documentation](https://codeql.github.com/docs/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)

---

## ⚖️ License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

**Remember: This is for EDUCATIONAL PURPOSES ONLY. Never use these patterns in production code.**
