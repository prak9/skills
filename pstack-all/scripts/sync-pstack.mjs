#!/usr/bin/env node

import { execFileSync } from "node:child_process";
import { cpSync, existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const PSTACK_DEST = join(ROOT, "pstack");
const UPSTREAM_META = join(ROOT, ".pstack-upstream.json");
const GENERATOR = join(ROOT, "scripts", "generate-pstack-harness-trees.mjs");

const args = process.argv.slice(2);
function getFlag(name, fallback) {
  const index = args.indexOf(name);
  if (index === -1 || index + 1 >= args.length) return fallback;
  return args[index + 1];
}

const repoUrl = getFlag("--repo", "https://github.com/cursor/plugins.git");
const ref = getFlag("--ref", "main");
const localSource = getFlag("--source", "");
const skipGenerate = args.includes("--no-generate");

let tmpDir = "";
let sourceRepo = localSource;

try {
  if (!sourceRepo) {
    tmpDir = mkdtempSync(join(tmpdir(), "pstack-sync-"));
    console.log(`Sparse-cloning pstack from ${repoUrl} (${ref})...`);
    execFileSync(
      "git",
      ["clone", "--depth=1", "--filter=blob:none", "--sparse", "--branch", ref, repoUrl, tmpDir],
      { stdio: "inherit" },
    );
    execFileSync("git", ["-C", tmpDir, "sparse-checkout", "set", "pstack"], { stdio: "inherit" });
    sourceRepo = tmpDir;
  }

  const sourcePstack = join(sourceRepo, "pstack");
  if (!existsSync(sourcePstack)) {
    throw new Error(`Expected pstack directory at ${sourcePstack}`);
  }

  let commit = "unknown";
  try {
    commit = execFileSync("git", ["-C", sourceRepo, "rev-parse", "HEAD"], { encoding: "utf8" }).trim();
  } catch {
    // Non-git local source directory
  }

  rmSync(PSTACK_DEST, { recursive: true, force: true });
  cpSync(sourcePstack, PSTACK_DEST, { recursive: true });

  const pluginJson = JSON.parse(readFileSync(join(PSTACK_DEST, "plugin.json"), "utf8"));
  const metadata = {
    repo: repoUrl.replace(/\.git$/, ""),
    path: "pstack",
    ref,
    commit,
    version: pluginJson.version ?? "unknown",
    syncedAt: new Date().toISOString(),
  };
  writeFileSync(UPSTREAM_META, `${JSON.stringify(metadata, null, 2)}\n`);
  console.log(`Synced pstack v${metadata.version} (${commit.slice(0, 12)}) into pstack/`);

  if (!skipGenerate) {
    execFileSync(process.execPath, [GENERATOR], { stdio: "inherit" });
  }
} finally {
  if (tmpDir) {
    rmSync(tmpDir, { recursive: true, force: true });
  }
}
