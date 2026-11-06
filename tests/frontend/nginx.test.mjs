// Regression tests for the Nginx configuration that fixed the 504 and /api path bugs.
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";

const ROOT = path.resolve(import.meta.dirname, "..", "..");
const conf = fs.readFileSync(path.join(ROOT, "frontend", "nginx.conf"), "utf8");

test("nginx resolves the backend name per request (fixes the 504)", () => {
  assert.match(conf, /resolver\s+169\.254\.169\.253/);
  assert.match(conf, /set\s+\$backend\s+"http:\/\/backend\.mediconnect\.local:8000"/);
  assert.match(conf, /proxy_pass\s+\$backend;/);
});

test("nginx strips the /api prefix before calling the backend", () => {
  assert.match(conf, /rewrite\s+\^\/api\/\(\.\*\)\$\s+\/\$1\s+break;/);
});

test("nginx forwards the client address headers", () => {
  assert.match(conf, /proxy_set_header\s+X-Forwarded-For/);
  assert.match(conf, /proxy_set_header\s+X-Real-IP/);
});

test("nginx serves the single page app with a fallback to index.html", () => {
  assert.match(conf, /try_files\s+\$uri\s+\$uri\/\s+\/index\.html/);
});
