// Unit tests for the frontend helper modules. Run with: node --test tests/frontend
// They use only Node's built-in test runner, so no extra packages are needed.
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { pathToFileURL } from "node:url";

const ROOT = path.resolve(import.meta.dirname, "..", "..");
const LIB = path.join(ROOT, "frontend", "src", "lib");

// ---- date.js is plain JavaScript, import it directly ----
const date = await import(pathToFileURL(path.join(LIB, "date.js")).href);

// ---- api.js needs axios and Vite's import.meta.env, so load a patched copy ----
const storage = new Map();
globalThis.localStorage = {
  getItem: (k) => (storage.has(k) ? storage.get(k) : null),
  setItem: (k, v) => storage.set(k, String(v)),
  removeItem: (k) => storage.delete(k),
};
let source = fs.readFileSync(path.join(LIB, "api.js"), "utf8");
source = source
  .replace('import axios from "axios";', "const axios = { create: (config) => ({ config }) };")
  .replace("import.meta.env.VITE_API_BASE_URL", "undefined");
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "mediconnect-api-"));
const tmpFile = path.join(tmp, "api.mjs");
fs.writeFileSync(tmpFile, source);
const api = await import(pathToFileURL(tmpFile).href);

test("toBackendDate converts YYYY-MM-DD to DD-MM-YYYY", () => {
  assert.equal(date.toBackendDate("2026-11-06"), "06-11-2026");
});

test("toBackendDate returns an empty string for empty input", () => {
  assert.equal(date.toBackendDate(""), "");
  assert.equal(date.toBackendDate(undefined), "");
});

test("todayIso returns today's date in ISO format", () => {
  assert.match(date.todayIso(), /^\d{4}-\d{2}-\d{2}$/);
  assert.equal(date.todayIso(), new Date().toISOString().slice(0, 10));
});

test("maxBookingIso is the given number of days after today", () => {
  const diff = (Date.parse(date.maxBookingIso(10)) - Date.parse(date.todayIso())) / 86400000;
  assert.equal(diff, 10);
});

test("api client defaults to the /api base path used behind Nginx", () => {
  assert.equal(api.api.config.baseURL, "/api");
});

test("extractList accepts a plain array", () => {
  assert.deepEqual(api.extractList([1, 2]), [1, 2]);
});

test("extractList reads items from a paginated response", () => {
  assert.deepEqual(api.extractList({ total: 1, items: ["a"] }), ["a"]);
});

test("extractList never returns a non-array (this prevented the page crash)", () => {
  assert.deepEqual(api.extractList(null), []);
  assert.deepEqual(api.extractList(undefined), []);
  assert.deepEqual(api.extractList({ total: 0 }), []);
  assert.deepEqual(api.extractList("text"), []);
});

test("extractErrorMessage handles string, list and missing details", () => {
  assert.equal(api.extractErrorMessage({ response: { data: { detail: "Bad" } } }), "Bad");
  assert.equal(
    api.extractErrorMessage({ response: { data: { detail: [{ msg: "A" }, { msg: "B" }] } } }),
    "A B"
  );
  assert.match(api.extractErrorMessage({}), /Something went wrong/);
});

test("tokens are stored per portal and cleared independently", () => {
  api.storeToken("patient", "abc");
  api.storeToken("admin", "xyz");
  assert.equal(api.getStoredToken("patient"), "abc");
  api.clearToken("patient");
  assert.equal(api.getStoredToken("patient"), null);
  assert.equal(api.getStoredToken("admin"), "xyz");
  api.clearToken("admin");
});

test("withAuth sends a bearer header only when a token exists", () => {
  api.clearToken("doctor");
  assert.deepEqual(api.withAuth("doctor"), {});
  api.storeToken("doctor", "tok");
  assert.deepEqual(api.withAuth("doctor"), { headers: { Authorization: "Bearer tok" } });
  api.clearToken("doctor");
});
