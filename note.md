Security note:

Add a state parameter (random token) to prevent CSRF and verify it in the callback.

Consider PKCE (code_challenge) for public clients (mobile/SPA). For server-side confidential clients PKCE is optional but safe.
