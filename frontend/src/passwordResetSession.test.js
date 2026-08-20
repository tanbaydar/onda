import assert from "node:assert/strict";
import test from "node:test";
import { clearPasswordResetEmail, readPasswordResetEmail, savePasswordResetEmail } from "./passwordResetSession.js";

function memoryStorage() {
  const values = new Map();
  return {
    getItem: (key) => values.get(key) ?? null,
    setItem: (key, value) => values.set(key, value),
    removeItem: (key) => values.delete(key),
  };
}

test("password reset email survives navigation state loss within the session", () => {
  const storage = memoryStorage();
  assert.equal(savePasswordResetEmail(" Reset@Example.COM ", storage), "reset@example.com");
  assert.equal(readPasswordResetEmail(storage), "reset@example.com");
});

test("password reset email is removed after completion", () => {
  const storage = memoryStorage();
  savePasswordResetEmail("reset@example.com", storage);
  clearPasswordResetEmail(storage);
  assert.equal(readPasswordResetEmail(storage), "");
});

test("unavailable session storage fails closed without blocking reset", () => {
  const storage = {
    getItem() { throw new Error("blocked"); },
    setItem() { throw new Error("blocked"); },
    removeItem() { throw new Error("blocked"); },
  };
  assert.equal(savePasswordResetEmail("reset@example.com", storage), "reset@example.com");
  assert.equal(readPasswordResetEmail(storage), "");
  assert.doesNotThrow(() => clearPasswordResetEmail(storage));
});
