# API lab results

Initial observations against https://quickpizza.grafana.com on 10 November 2026.
The full suite was revalidated on 11 November 2026 after switching to random,
ephemeral test passwords and removing credential-bearing request evidence.

## Part 0

- Step 0.1, the number of pizza names: 18.
- Step 0.3, status code of the request without a token: 401; body `{"error":"authentication failed"}`.
- Step 0.4, the name of my pizza: The Solid Margherita. Every returned ingredient was vegetarian.
- Step 0.12, three runs without a session: all three created the user (201), then failed login (401 instead of 200). The temporary test was removed as instructed.
- Step 0.16, blocks of "how many of the three tools are excluded": 0, 1, 2, 3. The original inputs covered only 1. Added `[]`, `["Knife", "Scissors"]`, and the all-three input. The all-three input is now a separate strict xfail.
- Curl observations and A2 request bodies are saved in `evidence/`.
- Step 0.6: changing the expected name to Pineapple Supreme produced the intended AssertionError; restoring Margherita passed. Step 0.14: the delete-rating test also passed when run alone.

## Defect report

- Title: Defect 1 - excluding all available tools causes an internal server error.
- Request: `POST /api/pizza`, authenticated as a newly created test user, `Content-Type: application/json`, body `{"excludedTools":["Knife","Pizza cutter","Scissors"]}`. A valid token must be obtained by creating/logging in a fresh user; no private token is published.
- Expected result: 400 with a nonempty JSON error message explaining that no pizza can satisfy the restrictions, as specified by the product owner.
- Actual result: 500 and an empty response body, confirmed using curl before implementing the regression test.
- Severity: Medium. A legitimate restriction combination crashes this request and prevents the client from explaining how to correct it; other request combinations remain usable. This observation alone does not prove the whole service crashes.
- Regression: `test_all_tools_excluded_is_refused`, marked `xfail(strict=True)`. It asserts the required 400 response and JSON message. A future fix becomes XPASS(strict), making the suite fail until the marker is reviewed/removed.

## Part A

- A2 curl messages: decimal stars -> 400, `json: cannot unmarshal number 3.5 into Go struct field Rating.stars of type int`; text stars -> 400, `json: cannot unmarshal string into Go struct field Rating.stars of type int`; missing stars -> 400, `number of stars must be between 1 and 5 (inclusive)`; nonexistent pizza -> 400, `pizza ID 999999999 not found`; absent/short token -> 401, `authentication failed`.
- Step A4, status codes when the other user reads, changes and deletes: GET 404, PUT 400, DELETE 400. In all three cases the owner could still read exactly the original rating.
- Latest full run: 32 passed, 1 xfailed, 0 errors in 53.64 seconds. The initial report was opened and checked in a browser; report.html now contains the revalidated run.
- Cleanup implementation note: DELETE of an already deleted rating answers 400 on this deployment. Teardown reads first and skips deletion when GET returns 404, so the deliberate delete test does not cause a spurious cleanup failure.

## Part B

1. Real API tests can detect broken integration between routing, JSON decoding and persistence (for example a successful update that is not stored), and deployment/authentication/load-balancer problems such as a login reaching a backend without the new user. Stubbed unit tests cannot exercise these real connections. Unit tests remain useful because they are fast, deterministic and can isolate rare error branches without network access.

2. A new unique user isolates each test from other students and from earlier cases. The public token shares state, so a passing/failing result could otherwise depend on someone else's work. For Project 2, create records/accounts with a unique group-and-run prefix, retain their IDs, modify only those records, and remove the group's own temporary data afterward. Read group credentials from environment variables.

3. A session preserves the AWSALB cookies set by the load balancer. QuickPizza's backends keep their own users, so keeping the cookie routes dependent create/login/rating calls to the same backend. Without a session, all three observed experiments created a user successfully but received 401 at login. This demonstrates the deployment dependency; it does not imply every future no-session run must fail.

4. Excluding all three tools revealed Defect 1. A 500 misrepresents a predictable invalid restriction combination as a server failure; an empty body supplies no machine-readable reason or actionable message and may also break a client's JSON decoder. A 400 with a JSON error allows the app to explain the input problem. The xfail preserves the required behavior and defect evidence, while strict=True signals when the implementation starts meeting that requirement.

5. Base choice needs 1+(3-1)+(4-1)+(2-1)+(3-1)=9 tests: one base plus each non-base block in turn. All combinations requires 3*4*2*3=72 model combinations. Some combinations involve inapplicable numeric-value characteristics for nonnumeric/missing stars, so 72 is the model's Cartesian count, not a claim that every combination is semantically independent.

6. The other user received GET 404, PUT 400 and DELETE 400. I would normally expect 403 for a valid user lacking ownership, or 404 if the API intentionally hides whether another user's record exists. The 400 responses are less specific, but a different 4xx code alone is not evidence that ownership protection failed: each test also checks that the owner can still read exactly the original rating. The lab permits any 4xx here, so these results meet its contract. If an API contract promises one precise code, violating that documented code would be a separate response-contract defect.

7. `curl -H "@madeup.txt" https://quickpizza.grafana.com/api/ratings` returned 200 with a `ratings` list containing 50 entries in this observation. The token was invented, not issued by login. This is an authentication defect: token length appears sufficient to pass this read operation, allowing unauthorized disclosure. On a real system, a stranger could read ratings without an account; depending on the returned fields this could expose users' activity or related identifiers. No write operation was attempted with the invented token, so these observations do not establish that it permits changes. Only the response shape/count was retained, not other users' rating details.

8. An API test directly checks exact HTTP codes, JSON field types and rejected inputs, including inputs a webpage may prevent users from entering. A browser test checks rendered layout, button behavior and whether a user actually sees the correct error message; an API-only test cannot observe those.
