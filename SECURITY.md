# Security

This repository is a starter. It does not run a hosted service, and it does not connect to a firm's complaints system.

## Reporting a vulnerability

Report a vulnerability in this code through [GitHub private vulnerability reporting](https://github.com/rahul-bachina/consumer-duty-complaints-copilot-agent/security/advisories/new).

If that page is not available, contact [Rahul Bachina on GitHub](https://github.com/rahul-bachina). Describe the issue. Do not include live complaint text, customer data, access keys, or passwords.

## What not to put in an issue

Do not open a public issue that contains:

- a real complaint, transcript, or customer record
- special-category data, including health information
- credentials, connection strings, or API keys

The fixtures in this repository are synthetic. The fictional firm is Northbridge Mutual.

## What this starter already refuses

The permissions manifest disables writes, sends, complaint decisions, redress, and a vulnerability label on the customer. The mock intake keeps the handler's receipt date when the complaint text tells it to move the date. Those controls are not a penetration test of a deployed agent. A firm that connects this starter to a tenant still has to review the manifest, the connectors, and the logging before anyone uses it on a live complaint.
