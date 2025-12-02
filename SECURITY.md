# Security Policy

## Supported Versions

We actively support the following versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability, please follow these steps:

### How to Report

1. **Do NOT open a public issue** for security vulnerabilities.

2. **Email the maintainers directly:**
   - Create a new issue on GitHub and mark it as a security vulnerability
   - Or contact the repository maintainers through GitHub

3. **Include the following information:**
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if you have one)

### What to Report

Please report any security issues related to:

- **Authentication vulnerabilities**: Issues with password handling, token storage, or encryption
- **Token storage security**: Problems with how authentication tokens are stored (file system, keyring)
- **API security**: Vulnerabilities in how the library communicates with the modem
- **Dependency vulnerabilities**: Security issues in dependencies that affect this library

### Response Time

We will do our best to respond to security reports in a timely manner. Please be patient as this is a community-maintained project.

### Disclosure Policy

- We aim to work with you to understand and resolve the issue
- We prefer not to disclose vulnerabilities publicly until a fix is available
- We will credit you for the discovery (unless you prefer to remain anonymous)

## Security Considerations

### Token Storage

This library stores authentication tokens to avoid repeated logins. By default, tokens are stored in:
- **File system**: `~/.alcatel_modem_session` (readable by the user only)
- **System keyring**: If available (recommended for better security)

**Security recommendations:**
- Use system keyring when available (install `keyring` package)
- Ensure proper file permissions on token storage files
- Do not commit token files to version control
- Consider using environment variables for passwords instead of storing them in config files

### Password Handling

- Passwords can be provided via:
  - Command-line arguments (visible in process list)
  - Configuration files (`~/.config/alcatel-api/config.toml`)
  - Environment variables (recommended for scripts)

**Best practices:**
- Use environment variables for automated scripts
- Avoid hardcoding passwords in code
- Use system keyring for interactive use
- Rotate passwords regularly

### Encryption Keys

The library uses hardcoded encryption keys that were reverse-engineered from Alcatel modem firmware. These keys are:
- Required for compatibility with Alcatel modems
- Not a security risk (they're used for client-side encryption only)
- Documented in the code with their origin

### Network Security

- The library communicates with modems over HTTP (not HTTPS)
- This is a limitation of the modem's API, not the library
- Ensure you're on a trusted network when using this library
- Consider using a VPN or secure network connection

## Known Limitations

1. **HTTP-only communication**: Modems typically use HTTP, not HTTPS
2. **Local network only**: The modem API is only accessible on the local network
3. **No encryption for API calls**: The modem API itself doesn't use encryption (beyond the custom encryption for credentials)

## Security Best Practices for Users

1. **Change default passwords**: Always change the default admin password on your modem
2. **Use trusted networks**: Only use this library on trusted networks
3. **Keep dependencies updated**: Regularly update the library and its dependencies
4. **Monitor access**: Check modem logs if available
5. **Use keyring**: Install and use the `keyring` package for better token storage security

## Questions?

If you have security questions or concerns, please open an issue or contact the maintainers.

