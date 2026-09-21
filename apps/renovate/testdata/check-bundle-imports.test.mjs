import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

const checker = fileURLToPath(new URL("./check-bundle-imports.mjs", import.meta.url));

test("static import checks ignore prose but detect missing dependencies", (t) => {
  const root = mkdtempSync(path.join(tmpdir(), "renovate-imports-"));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  mkdirSync(path.join(root, "dist"));

  // Meet the scan's minimum using packages that exist only in this fixture.
  const imports = [];
  for (let i = 0; i < 20; i++) {
    const pkg = `fixture-${i}`;
    const dir = path.join(root, "node_modules", pkg);
    mkdirSync(dir, { recursive: true });
    writeFileSync(path.join(dir, "package.json"), JSON.stringify({ name: pkg }));
    imports.push(`import "${pkg}";`);
  }
  const source = `${imports.join("\n")}
    // Transition from 'oldLabels' to 'newLabels'.
    /* import "comment-only"; */
    const example = 'import "string-only";';
    const template = \`export * from "template-only";\`;
    const pattern = /from "regex-only"/;
    import("dynamic-only");
    throw new Error("the checker must never evaluate the bundle");
  `;
  const file = path.join(root, "dist", "index.js");
  const run = () => spawnSync(process.execPath, ["--experimental-vm-modules", checker, root], { encoding: "utf8" });

  writeFileSync(file, source);
  let result = run();
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /20 external package\(s\) imported/);

  // Exercise each static form, including multiline imports and re-exports.
  for (const declaration of [
    'import {\n stripIndent\n} from "common-tags";',
    'export { stripIndent } from "common-tags";',
    'export * from "common-tags";',
    'import "common-tags";',
  ]) {
    writeFileSync(file, `${source}\n${declaration}`);
    result = run();
    assert.equal(result.status, 1, result.stderr);
    assert.match(result.stderr, /common-tags -- imported from/);
  }

  writeFileSync(file, '// from "oldLabels"');
  result = run();
  assert.equal(result.status, 1, result.stderr);
  assert.match(result.stderr, /only 0 external package\(s\) found/);
});
