# Security notes

Implemented controls include Argon2 password hashing, random server-side sessions stored as SHA-256 token hashes, HttpOnly/SameSite cookies, production Secure cookies, backend authorization, exact-Origin and custom-header checks on admin mutations, request-size/deadline limits, parameterized SQLAlchemy queries, React text rendering, same-origin frontend API access, source allowlists, pinned public source IP connections preserving TLS SNI, redirect refusal, bounded robots/document downloads, source publication gates and citation-ID validation.

Retrieved content, uploaded text and chat history remain untrusted. The model has no code, database or external-action tools. Citation identifiers outside the evidence set reject the entire generated answer. Strict JSON types reject malformed provider responses. These controls do not prove semantic correctness of an LLM answer.

## Important operating limits
- Keep one API worker until rate limiting moves to a shared store. Current limiter keys use the actual socket peer and do not trust arbitrary forwarding headers.
- A large PDF can consume CPU despite byte/page limits. For public-scale administration, move extraction to a sandboxed worker with CPU and memory quotas, antivirus scanning and an asynchronous job queue.
- Enforce egress rules and public ingress limits at the host as defense in depth.
- Rotate credentials and use a managed secret store in production.
- Admin login has no MFA or multi-role delegation in this release. Do not share administrator credentials.
- Review modal keyboard focus trapping and a complete accessibility audit remain outstanding.
- No citizen identity-document upload or application submission is implemented.
- Feedback and audit retention is operator-managed. Publish a retention schedule and deletion procedure before collecting public submissions.

No automated system can certify this application secure merely from passing tests. Test the deployed boundary and use an independent review before a public launch.
