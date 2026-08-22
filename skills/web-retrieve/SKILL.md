---
name: web-retrieve
description: Retrieve public web content with a minimal fallback when normal HTTP requests are blocked. Use for content retrieval and research, not for testing or debugging real HTTP/API behavior.
---

# Web Retrieve

Use this skill when the goal is to obtain publicly accessible web content and a normal HTTP request is blocked or returns an obvious bot-filter response.

Do not use this skill when the task is to test, reproduce, inspect, or debug the actual HTTP behavior of an application, API, authentication flow, CDN, WAF, cache, or client. In those cases, preserve the real client behavior unless the user explicitly asks to test another identity.

## Retrieval policy

Keep the fallback deliberately small:

1. **Normal request** — use the normal/default HTTP client behavior first.
2. **Browser-like retry** — if the normal request fails because of automated-client filtering (for example 403, 429, or an obvious bot-block page), retry once using a normal modern browser identity or an available browser tool.
3. **Change source** — if the browser-like retry still fails, use another public source instead of escalating the impersonation stack.

The objective is to obtain the needed public information, not to defeat a particular site's anti-bot system.

## Boundaries

- Do not make a special AI crawler or vendor identity the default User-Agent.
- Do not impersonate identities such as OpenAI, xAI, Claude, Googlebot, WhatsApp, or other named services as a standing fallback.
- Do not automatically escalate to TLS fingerprint spoofing, captcha solving, proxy rotation, or other anti-bot bypass techniques.
- Do not use User-Agent substitution to bypass authentication, account permissions, private resources, or explicit access controls.
- Do not treat a response obtained with a browser-like retry as proof that the resource works normally for the original client.
- Respect rate limits and stop when repeated retrieval would be abusive or clearly unwelcome.

## Execution guidance

For command-line retrieval, preserve the default request first. Only add a browser-like identity on the single fallback retry.

Prefer a real browser/browser tool when one is already available. If only a raw HTTP client is available, use a normal modern browser User-Agent rather than a named AI crawler identity.

When the fallback succeeds, continue the user's task normally. Mention the alternate retrieval path only when it matters to the result, reproducibility, or debugging context.

When both attempts fail, switch sources. Do not keep stacking increasingly aggressive bypass techniques unless the user explicitly changes the task from retrieval to diagnostics or anti-bot research.

## Decision rule

Use this simple distinction:

- **FETCH mode:** the goal is the public content → normal request → one browser-like retry → another source.
- **TEST mode:** the goal is real HTTP behavior → do not alter request identity automatically.
