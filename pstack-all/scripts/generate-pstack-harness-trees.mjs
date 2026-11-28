#!/usr/bin/env node

import { chmodSync, existsSync, mkdirSync, readdirSync, readFileSync, rmSync, statSync, writeFileSync } from "node:fs";
import { dirname, join, posix, relative } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const PSTACK = join(ROOT, "pstack");
const SKILLS = join(PSTACK, "skills");
const OUT = join(ROOT, "harness", "pstack");
const GUIDE = "docs/guide";
const COMMAND = "node scripts/generate-pstack-harness-trees.mjs";
const GITHUB = "https://github.com/cursor/plugins";
const LINK = /\]\(([^)\s]+)\)/g;

const TARGETS = [
  {
    name: "claude-code",
    displayName: "Claude Code",
    adapterSource: join(PSTACK, "docs", "harness", "claude-code.md"),
    adapterDest: "docs/harness/claude-code.md",
    manifests: ["plugin.json", ".claude-plugin/plugin.json"],
    includeLogo: false,
    transformAgent: null,
    buildManifest: (baseManifest) => Buffer.from(`${JSON.stringify(baseManifest, null, 2)}\n`),
  },
  {
    name: "antigravity",
    displayName: "Antigravity",
    adapterSource: join(ROOT, "adapters", "antigravity.md"),
    adapterDest: "docs/harness/antigravity.md",
    manifests: ["plugin.json", ".antigravity-plugin/plugin.json"],
    includeLogo: true,
    transformAgent: transformAntigravityAgent,
    buildManifest: buildAntigravityManifest,
  },
];

const README = `# pstack harness trees

This folder is generated from \`pstack/\` and \`adapters/antigravity.md\`. Do not edit it by hand.

- Cursor uses \`pstack/\` directly.
- Claude Code installs \`claude-code/\`.
- Antigravity installs \`antigravity/\`.

Each harness tree leaves out Cursor-only directories such as \`pstack/automations\`. A relative link to a pstack file that a tree leaves out points at that file on GitHub \`main\` instead.

After syncing \`pstack/\` or editing \`adapters/antigravity.md\`, run \`${COMMAND}\` from the repository root and commit the result.
`;

const TERMS = [
  { key: "`Task`", re: /`Task`|\bTask (tool|subagent|call)/ },
  { key: "`AskQuestion`", re: /AskQuestion/ },
  { key: "todolist", re: /\btodo ?list\b/i },
  { key: "generalPurpose", re: /generalPurpose/ },
  { key: "poteto-agent", re: /poteto-agent/ },
  { key: "comment-sicko", re: /comment-sicko/ },
  { key: "`readonly: true`", re: /readonly: (true|false)|readonly\/Ask/ },
  { key: "`environment: \"cloud\"`", re: /environment: "(cloud|local)"/ },
  { key: "cloud_base_branch", re: /cloud_base_branch/ },
  { key: "`run_in_background: true`", re: /run_in_background/ },
  { key: "`resume`", re: /`resume`/ },
  { key: "`file_attachments`", re: /file_attachments/ },
  { key: "claude-", re: /\bclaude-[a-z]+-\d/ },
  { key: "grok-", re: /\bgrok-\d/ },
  { key: "gpt-", re: /\bgpt-\d/ },
  { key: "inherit-parent", re: /inherit-parent/ },
  { key: "pstack-models.mdc", re: /pstack-models\.mdc/ },
  { key: ".cursor/skills/", re: /\.cursor\/skills/ },
  { key: "~/.cursor/plugins/", re: /\.cursor\/plugins|\.cursor-plugin/ },
  { key: ".cursor/rules/", re: /\.cursor\/rules|always-applied rule/ },
  { key: "agent-transcripts", re: /agent-transcripts|\.cursor\/projects/ },
  { key: "Cursor-only features", re: /Bugbot|Cursor [Aa]utomation|cursor\.(sh|com)\/automations|[Cc]loud [Aa]gent|built-in PR tool/ },
];
const ROUTE_KEY = "Run another pstack skill";
const SKILL_NAME = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

function buildAntigravityManifest(baseManifest) {
  const manifest = {
    $schema: "https://antigravity.google/schemas/v1/plugin.json",
    name: baseManifest.name,
    displayName: baseManifest.displayName ?? baseManifest.name,
    version: baseManifest.version,
    description: baseManifest.description,
    logo: "assets/logo.png",
    suggestedPrompts: [
      "/setup-pstack",
      "/poteto-mode",
      "/poteto-help",
    ],
  };
  return Buffer.from(`${JSON.stringify(manifest, null, 2)}\n`);
}

function transformAntigravityAgent(relPath, content) {
  const match = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!match) return content;

  const [, rawFrontmatter, rawBody] = match;
  const fmLines = rawFrontmatter
    .split("\n")
    .filter((line) => !/^(is_background|model|subagent|mainAgent):/.test(line));
  fmLines.push("subagent: true", "mainAgent: false", "model: inherit");

  let body = rawBody;
  if (relPath === "agents/poteto-agent.md") {
    body = body
      .replace(
        /search `~\/\.cursor\/plugins\/` for a file whose path ends in `skills\/poteto-mode\/SKILL\.md`\. If more than one file matches, use the copy whose `\.cursor-plugin\/plugin\.json` has the highest `version`\./,
        "search `~/.gemini/config/plugins/` and `.agents/plugins/` for a file whose path ends in `skills/poteto-mode/SKILL.md`. If more than one file matches, use the copy whose `.antigravity-plugin/plugin.json` or `plugin.json` has the highest `version`. Also read the sibling `docs/harness/antigravity.md` adapter once per session.",
      )
      .replace(/every Task spawn/g, "every subagent spawn");
  }

  return `---\n${fmLines.join("\n")}\n---\n${body}`;
}

function walk(dir) {
  return readdirSync(dir).flatMap((name) => {
    if (name === ".DS_Store" || name === "node_modules") return [];
    const path = join(dir, name);
    return statSync(path).isDirectory() ? walk(path) : [path];
  });
}

function file(path) {
  return { bytes: readFileSync(path), executable: (statSync(path).mode & 0o111) !== 0 };
}

if (!existsSync(SKILLS)) {
  console.error("FAIL pstack/skills does not exist. Run `node scripts/sync-pstack.mjs` first.");
  process.exit(1);
}

const skills = readdirSync(SKILLS).filter((name) => existsSync(join(SKILLS, name, "SKILL.md")));

function classify(skill) {
  const dir = join(SKILLS, skill);
  const others = skills.filter((name) => name !== skill).join("|");
  const route = new RegExp(`the \\*\\*(?<bold>${others})\\*\\* skill|\`/(?<command>${others})\``, "g");
  const linksToSkill = (line, name) => line.includes(`(../${name}/`);
  const namesBareSkill = (line) =>
    [...line.matchAll(route)].some(({ groups }) => !linksToSkill(line, groups.bold ?? groups.command));
  const usesCursorNames = new Set();
  for (const path of walk(dir).filter((path) => path.endsWith(".md"))) {
    const text = readFileSync(path, "utf8");
    for (const term of TERMS) if (term.re.test(text)) usesCursorNames.add(term.key);
    if (text.split("\n").some(namesBareSkill)) usesCursorNames.add(ROUTE_KEY);
  }
  const text = readFileSync(join(dir, "SKILL.md"), "utf8");
  const wrap = usesCursorNames.size > 0 && /^# /m.test(text);
  return { usesCursorNames, wrap };
}

const classes = new Map(skills.map((skill) => [skill, classify(skill)]));
const problems = [];
const users = new Map();
for (const [skill, { usesCursorNames, wrap }] of classes) {
  if (usesCursorNames.size > 0 && !wrap) problems.push(`skills/${skill}/SKILL.md uses Cursor names but has no H1`);
  for (const key of usesCursorNames) users.set(key, [...(users.get(key) ?? []), skill]);
  const frontmatter = readFileSync(join(SKILLS, skill, "SKILL.md"), "utf8").match(/^---\n([\s\S]*?)\n---/)?.[1] ?? "";
  const name = frontmatter.match(/^name:(.*)$/m)?.[1].trim().replace(/^(["'])(.*)\1$/, "$2");
  if (name !== skill) problems.push(`skills/${skill}/SKILL.md has name ${JSON.stringify(name ?? "")}, not its folder name ${skill}`);
  if (!SKILL_NAME.test(skill) || skill.length > 64) problems.push(`skills/${skill} is not lowercase words joined by hyphens, at most 64 characters`);
}

for (const target of TARGETS) {
  if (!existsSync(target.adapterSource)) {
    problems.push(`${target.displayName} adapter is missing at ${relative(ROOT, target.adapterSource)}`);
    continue;
  }
  const adapter = readFileSync(target.adapterSource, "utf8");
  for (const [key, using] of users) {
    if (!adapter.includes(key)) {
      problems.push(`${target.displayName} adapter has no row for ${key}, used by ${using.join(", ")}`);
    }
  }
}

for (const problem of problems) console.log(`FAIL ${problem}`);
if (problems.length > 0) process.exit(1);

function resolve(from, href) {
  const target = href.replace(/[#?].*/, "");
  if (!target || /^[a-z][a-z0-9+.-]*:/i.test(target)) return undefined;
  const path = posix.join(posix.dirname(from), target).replace(/\/$/, "");
  return existsSync(join(PSTACK, path)) ? path : undefined;
}

function has(files, path) {
  return files.has(path) || [...files.keys()].some((key) => key.startsWith(`${path}/`));
}

const baseManifest = JSON.parse(readFileSync(join(PSTACK, "plugin.json"), "utf8"));

function renderTarget(target) {
  const copies = [
    ...walk(SKILLS),
    ...walk(join(PSTACK, "agents")),
    ...walk(join(PSTACK, GUIDE)),
    join(PSTACK, "README.md"),
  ];
  const files = new Map(copies.map((path) => [relative(PSTACK, path), file(path)]));
  files.set(target.adapterDest, file(target.adapterSource));

  if (target.includeLogo && existsSync(join(PSTACK, "assets", "logo.png"))) {
    files.set("assets/logo.png", file(join(PSTACK, "assets", "logo.png")));
  }

  const line =
    `In ${target.displayName}, read [the ${target.displayName} adapter](../../${target.adapterDest}) once per session before you follow this skill. ` +
    `It maps the Cursor names in pstack skills to ${target.displayName}.`;
  for (const [skill, { wrap }] of classes) {
    const path = `skills/${skill}/SKILL.md`;
    const text = files.get(path).bytes.toString("utf8");
    if (wrap) files.get(path).bytes = Buffer.from(text.replace(/^(# .*)\n+/m, `$1\n\n${line}\n\n`));
  }

  if (target.transformAgent) {
    for (const [path, entry] of files) {
      if (path.startsWith("agents/") && path.endsWith(".md")) {
        const transformed = target.transformAgent(path, entry.bytes.toString("utf8"));
        entry.bytes = Buffer.from(transformed);
      }
    }
  }

  files.set("LICENSE", file(join(PSTACK, "LICENSE")));
  const manifestBytes = target.buildManifest(baseManifest);
  for (const manifest of target.manifests) {
    files.set(manifest, { bytes: manifestBytes, executable: false });
  }

  for (const [path, entry] of files) {
    if (!path.endsWith(".md")) continue;
    const text = entry.bytes.toString("utf8").replace(LINK, (link, href) => {
      const resolved = resolve(path, href);
      if (!resolved || resolved.split("/")[0] === ".." || has(files, resolved)) return link;
      const kind = statSync(join(PSTACK, resolved)).isDirectory() ? "tree" : "blob";
      return `](${GITHUB}/${kind}/main/pstack/${resolved}${href.slice(href.search(/[#?]|$/))})`;
    });
    entry.bytes = Buffer.from(text);
  }

  return files;
}

const rendered = new Map([["README.md", { bytes: Buffer.from(README), executable: false }]]);
const dangling = [];

for (const target of TARGETS) {
  const files = renderTarget(target);
  for (const [path, entry] of files) {
    rendered.set(`${target.name}/${path}`, entry);
    if (!path.endsWith(".md")) continue;
    for (const [, href] of entry.bytes.toString("utf8").matchAll(LINK)) {
      const resolved = resolve(path, href);
      if (resolved && !has(files, resolved)) {
        dangling.push(`harness/pstack/${target.name}/${path} links to ${href}, which is not in the tree`);
      }
    }
  }
}

for (const link of dangling) console.log(`FAIL ${link}`);
if (dangling.length > 0) process.exit(1);

if (process.argv.includes("--check")) {
  const onDisk = new Map(existsSync(OUT) ? walk(OUT).map((path) => [relative(OUT, path), file(path)]) : []);
  const drifted = [...new Set([...rendered.keys(), ...onDisk.keys()])].sort().filter((path) => {
    const [want, have] = [rendered.get(path), onDisk.get(path)];
    return !want || !have || !want.bytes.equals(have.bytes) || want.executable !== have.executable;
  });
  for (const path of drifted.slice(0, 20)) console.log(`harness/pstack/${path}`);
  if (drifted.length > 0) {
    console.log(`harness/pstack is out of date. Run \`${COMMAND}\` and commit the result.`);
    process.exit(1);
  }
  console.log("harness/pstack is up to date.");
} else {
  rmSync(OUT, { recursive: true, force: true });
  for (const [path, { bytes, executable }] of rendered) {
    mkdirSync(dirname(join(OUT, path)), { recursive: true });
    writeFileSync(join(OUT, path), bytes);
    chmodSync(join(OUT, path), executable ? 0o755 : 0o644);
  }
  const wrapped = [...classes.values()].filter(({ wrap }) => wrap).length;
  const targetNames = TARGETS.map((t) => t.name).join(", ");
  console.log(`${skills.length} skills, ${wrapped} SKILL.md files with adapter line (${targetNames})`);
}
