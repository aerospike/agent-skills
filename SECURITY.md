# Security Policy

## Supported Versions

<!-- Update this section with the versions of your project that are currently supported with security updates -->

| Version | Supported |
| ------- | --------- |
| 1.x.x   | Yes       |

## Reporting a Vulnerability

The Aerospike team takes security bugs seriously. We appreciate your efforts to responsibly disclose your findings.

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to **prodsec@aerospike.com**.

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

Please include the following information in your report:

- Type of issue (e.g., buffer overflow, SQL injection, cross-site scripting, authentication bypass, authorization flaw, information disclosure, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it
- Potential severity assessment (if applicable)

This information will help us triage your report more quickly.

## Scope

### In Scope

Security vulnerabilities in the following areas are within scope for reporting:

- Application code vulnerabilities (injection flaws, authentication/authorization issues, cryptographic weaknesses, etc.)
- API security vulnerabilities (improper access controls, rate limiting issues, input validation flaws, etc.)
- Configuration vulnerabilities (exposed sensitive information, insecure defaults, etc.)
- Cloud infrastructure security issues (misconfigurations, exposed resources, etc.)
- Dependency vulnerabilities in actively maintained components
- Data protection and encryption issues
- Denial of service vulnerabilities that significantly impact service availability

### Out of Scope

The following are not considered security vulnerabilities for the purposes of responsible disclosure:

- Physical security issues
- Social engineering attacks
- Denial of service attacks that require significant resources or are not exploitable through standard usage
- Issues requiring physical access to infrastructure
- Issues in third-party services that are outside of Aerospike's direct control
- Issues that require unlikely user interaction or configuration

## Security Response Process

Upon receiving a security vulnerability report, our security team will:

1. **Acknowledge receipt** within 72 hours
2. **Initial triage** within 5 business days to assess severity and validity
3. **Investigation** to confirm and understand the issue
4. **Remediation** development and testing
5. **Coordination** with reporter on disclosure timeline
6. **Security advisory** publication when appropriate

Critical vulnerabilities will receive expedited handling. We will provide regular updates to the reporter throughout the process.

## Security Practices

### Code Security

All code contributions are subject to security review. Contributors should:

- Follow secure coding practices and avoid common vulnerabilities (OWASP Top 10, CWE Top 25)
- Avoid hardcoding sensitive information such as credentials, API keys, or tokens
- Implement proper input validation and output encoding
- Use parameterized queries and prepared statements to prevent injection attacks
- Follow the principle of least privilege for access controls
- Implement proper error handling that does not leak sensitive information

### Dependency Management

We actively monitor and update dependencies to address security vulnerabilities:

- Dependencies are regularly scanned for known vulnerabilities
- Security updates are prioritized and applied in a timely manner
- All dependency updates are tested before deployment

### API Security

- Authentication and authorization mechanisms are enforced at all API endpoints
- Rate limiting is implemented to prevent abuse
- Input validation is performed on all API inputs
- API responses do not expose sensitive information

## Security Updates

Security updates will be released as part of our standard release process. Critical security vulnerabilities may result in out-of-cycle security releases. Security advisories will be published detailing the nature of the vulnerability and the remediation steps taken.

## Preferred Languages

We prefer all communications to be in English.

## Policy

Aerospike follows the principle of [Responsible Disclosure](https://en.wikipedia.org/wiki/Responsible_disclosure). We ask that security researchers:

- Act in good faith to avoid privacy violations, data destruction, and service interruption
- Keep vulnerability details confidential until we have resolved the issue and agreed upon disclosure timing
- Do not access or modify data that does not belong to you
- Provide us with a reasonable amount of time to address the issue before public disclosure

We will acknowledge researchers who responsibly disclose vulnerabilities, if they so desire, in our security advisories.
