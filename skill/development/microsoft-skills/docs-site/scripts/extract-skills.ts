import * as fs from "fs";
import * as path from "path";
import matter from "gray-matter";

function preprocessYamlFrontmatter(content: string): string {
  const match = content.match(/^---\n([\s\S]*?)\n---/);
  if (!match) return content;

  const frontmatter = match[1];
  const fixedFrontmatter = frontmatter.replace(
    /^(\s*package:\s*)(@.+)$/gm,
    '$1"$2"'
  );

  return content.replace(frontmatter, fixedFrontmatter);
}

interface Skill {
  name: string;
  description: string;
  package?: string;
  lang: "py" | "dotnet" | "ts" | "java" | "rust" | "core";
  category: string;
  path: string;
}

interface SkillFrontmatter {
  name?: string;
  description?: string;
  package?: string;
}

const LANG_MAP: Record<string, Skill["lang"]> = {
  python: "py",
  dotnet: "dotnet",
  typescript: "ts",
  java: "java",
  rust: "rust",
  core: "core",
};

/**
 * Infer the category from a skill name. Categories must match the values in
 * docs-site/src/components/CategoryTabs.tsx so the filter UI can group skills.
 *
 * Order matters — first match wins. More specific patterns come first.
 */
function inferCategory(name: string): string {
  // Foundry orchestrator + sub-skills (language-agnostic)
  if (name === "microsoft-foundry" || name.startsWith("foundry-")) return "foundry";

  // Foundry SDKs and AI services that are part of the Foundry surface
  if (name.startsWith("agent-framework-")) return "foundry";
  if (name.startsWith("azure-ai-projects-")) return "foundry";
  if (name.startsWith("azure-ai-agents-")) return "foundry";
  if (name.startsWith("azure-ai-openai")) return "foundry";
  if (name.startsWith("azure-ai-voicelive")) return "foundry";
  if (name.startsWith("azure-ai-contentsafety")) return "foundry";
  if (name.startsWith("azure-ai-contentunderstanding")) return "foundry";
  if (name.startsWith("azure-ai-document-intelligence")) return "foundry";
  if (name.startsWith("azure-ai-formrecognizer")) return "foundry";
  if (name.startsWith("azure-ai-textanalytics")) return "foundry";
  if (name.startsWith("azure-ai-translation")) return "foundry";
  if (name.startsWith("azure-ai-vision")) return "foundry";
  if (name.startsWith("azure-ai-anomalydetector")) return "foundry";
  if (name.startsWith("azure-ai-language")) return "foundry";
  if (name.startsWith("azure-ai-transcription")) return "foundry";
  if (name.startsWith("azure-ai-ml")) return "foundry";
  if (name.startsWith("azure-speech-to-text")) return "foundry";
  if (name.startsWith("azure-search-documents")) return "foundry";
  if (name === "azure-ai") return "foundry";
  if (name === "azure-aigateway") return "foundry";

  // M365
  if (name.startsWith("m365-")) return "m365";

  // Communications
  if (name.startsWith("azure-communication-")) return "communication";

  // Messaging / eventing
  if (name.startsWith("azure-eventhub")) return "messaging";
  if (name.startsWith("azure-eventgrid")) return "messaging";
  if (name.startsWith("azure-servicebus")) return "messaging";
  if (name.startsWith("azure-messaging-webpubsub")) return "messaging";
  if (name.startsWith("azure-web-pubsub")) return "messaging";
  if (name === "azure-messaging") return "messaging";

  // Identity
  if (name.startsWith("azure-identity")) return "entra";
  if (name.startsWith("entra-")) return "entra";
  if (name.includes("authentication-events")) return "entra";

  // Monitoring / observability
  if (name.startsWith("azure-monitor-")) return "monitoring";
  if (name.startsWith("appinsights-")) return "monitoring";
  if (name.startsWith("applicationinsights-")) return "monitoring";
  if (name.startsWith("azure-mgmt-applicationinsights")) return "monitoring";
  if (name === "azure-diagnostics") return "monitoring";
  if (name === "azure-kusto") return "monitoring";
  if (name === "kql") return "monitoring";

  // Data / storage / databases
  if (name.startsWith("azure-cosmos")) return "data";
  if (name.startsWith("azure-storage")) return "data";
  if (name.startsWith("azure-data-tables")) return "data";
  if (name.startsWith("azure-postgres")) return "data";
  if (name.startsWith("azure-resource-manager-cosmosdb")) return "data";
  if (name.startsWith("azure-resource-manager-mysql")) return "data";
  if (name.startsWith("azure-resource-manager-postgresql")) return "data";
  if (name.startsWith("azure-resource-manager-redis")) return "data";
  if (name.startsWith("azure-resource-manager-sql")) return "data";

  // Compute / orchestration / containers
  if (name.startsWith("azure-compute")) return "compute";
  if (name.startsWith("azure-containerregistry")) return "compute";
  if (name === "azure-kubernetes") return "compute";
  if (name === "airunway-aks-setup") return "compute";
  if (name.startsWith("azure-microsoft-playwright-testing")) return "compute";
  if (name.startsWith("azure-resource-manager-playwright")) return "compute";
  if (name.startsWith("azure-resource-manager-durabletask")) return "compute";
  if (name.startsWith("azure-maps-")) return "compute";

  // Integration & management (KeyVault, AppConfig, API Mgmt, etc.)
  if (name.startsWith("azure-keyvault")) return "integration";
  if (name.startsWith("azure-security-keyvault")) return "integration";
  if (name.startsWith("azure-appconfiguration")) return "integration";
  if (name.startsWith("azure-mgmt-apicenter")) return "integration";
  if (name.startsWith("azure-mgmt-apimanagement")) return "integration";
  if (name.startsWith("azure-mgmt-botservice")) return "integration";
  if (name.startsWith("azure-mgmt-fabric")) return "integration";
  if (name === "azure-resource-lookup") return "integration";
  if (name === "azure-resource-visualizer") return "integration";

  // Partner / third-party offerings managed via Azure mgmt
  if (name.startsWith("azure-mgmt-mongodbatlas")) return "partner";
  if (name.startsWith("azure-mgmt-arizeaiobservabilityeval")) return "partner";
  if (name.startsWith("azure-mgmt-weightsandbiases")) return "partner";

  // Frontend / web app patterns
  if (name === "frontend-design-review") return "frontend";
  if (name.startsWith("frontend-")) return "frontend";
  if (name.startsWith("react-")) return "frontend";
  if (name.startsWith("zustand-")) return "frontend";
  if (name === "github-primer-brand") return "frontend";
  if (name.startsWith("pydantic-")) return "frontend";
  if (name.startsWith("fastapi-")) return "frontend";

  // Default: general-purpose tooling, infra workflows, scaffolding, learning
  return "general";
}

const SUFFIX_MAP: Record<string, Skill["lang"]> = {
  "-py": "py",
  "-dotnet": "dotnet",
  "-ts": "ts",
  "-java": "java",
  "-rust": "rust",
};

function inferLangFromName(skillName: string): Skill["lang"] {
  for (const [suffix, lang] of Object.entries(SUFFIX_MAP)) {
    if (skillName.endsWith(suffix)) {
      return lang;
    }
  }
  return "core";
}

function findSymlinkInfo(
  skillName: string,
  skillsDir: string
): { lang: Skill["lang"]; category: string } | null {
  if (!fs.existsSync(skillsDir)) return null;
  const langDirs = fs.readdirSync(skillsDir);

  for (const langDir of langDirs) {
    const langPath = path.join(skillsDir, langDir);
    if (!fs.statSync(langPath).isDirectory()) continue;

    const categoryDirs = fs.readdirSync(langPath);
    for (const categoryDir of categoryDirs) {
      const categoryPath = path.join(langPath, categoryDir);
      if (!fs.statSync(categoryPath).isDirectory()) continue;

      const links = fs.readdirSync(categoryPath);
      for (const link of links) {
        const linkPath = path.join(categoryPath, link);
        try {
          const stat = fs.lstatSync(linkPath);
          if (stat.isSymbolicLink()) {
            const target = fs.readlinkSync(linkPath);
            const targetSkillName = path.basename(target);
            if (targetSkillName === skillName) {
              const lang = LANG_MAP[langDir] || "core";
              return { lang, category: categoryDir };
            }
          }
        } catch {
          continue;
        }
      }
    }
  }
  return null;
}

const PLUGIN_LANG_MAP: Record<string, Skill["lang"]> = {
  "azure-sdk-python": "py",
  "azure-sdk-dotnet": "dotnet",
  "azure-sdk-typescript": "ts",
  "azure-sdk-java": "java",
  "azure-sdk-rust": "rust",
};

function extractSkillFromDir(
  skillDir: string,
  skillPath: string,
  repoRelativePath: string,
  lang: Skill["lang"],
  category: string
): Skill | null {
  const skillMdPath = path.join(skillPath, "SKILL.md");
  if (!fs.existsSync(skillMdPath)) return null;

  try {
    const rawContent = fs.readFileSync(skillMdPath, "utf-8");
    const content = preprocessYamlFrontmatter(rawContent);
    const { data } = matter(content);
    const frontmatter = data as SkillFrontmatter;

    if (!frontmatter.name) {
      console.warn(`Skipping ${skillDir}: missing name in frontmatter`);
      return null;
    }

    const skill: Skill = {
      name: frontmatter.name,
      description: frontmatter.description || frontmatter.name,
      lang,
      category,
      path: repoRelativePath,
    };

    if (frontmatter.package) {
      skill.package = frontmatter.package;
    }

    return skill;
  } catch (err) {
    console.warn(`Skipping ${skillDir}: ${(err as Error).message}`);
    return null;
  }
}

function extractSkills(): Skill[] {
  const projectRoot = path.resolve(import.meta.dirname, "../..");
  const pluginsDir = path.join(projectRoot, ".github/plugins");
  const skillsSourceDir = path.join(projectRoot, ".github/skills");
  const skillsSymlinkDir = path.join(projectRoot, "skills");

  const skills: Skill[] = [];
  const seen = new Set<string>();

  // 1. Scan plugin bundles: .github/plugins/azure-sdk-*/skills/
  if (fs.existsSync(pluginsDir)) {
    for (const pluginName of fs.readdirSync(pluginsDir)) {
      const lang = PLUGIN_LANG_MAP[pluginName];
      if (!lang) continue;

      const pluginSkillsDir = path.join(pluginsDir, pluginName, "skills");
      if (!fs.existsSync(pluginSkillsDir)) continue;

      for (const skillDir of fs.readdirSync(pluginSkillsDir)) {
        const skillPath = path.join(pluginSkillsDir, skillDir);
        if (!fs.statSync(skillPath).isDirectory()) continue;

        const repoRelativePath = `.github/plugins/${pluginName}/skills/${skillDir}`;

        // Use symlink info from skills/ for category if available;
        // otherwise infer from the skill name.
        const symlinkInfo = findSymlinkInfo(skillDir, skillsSymlinkDir);
        const category = symlinkInfo?.category || inferCategory(skillDir);

        const skill = extractSkillFromDir(skillDir, skillPath, repoRelativePath, lang, category);
        if (skill) {
          skills.push(skill);
          seen.add(skillDir);
        }
      }
    }
  }

  // 2. Scan core skills still in .github/skills/ (real directories, not symlinks)
  if (fs.existsSync(skillsSourceDir)) {
    for (const skillDir of fs.readdirSync(skillsSourceDir)) {
      if (seen.has(skillDir)) continue;

      const skillPath = path.join(skillsSourceDir, skillDir);
      if (!fs.statSync(skillPath).isDirectory()) continue;

      const repoRelativePath = `.github/skills/${skillDir}`;
      const lang = inferLangFromName(skillDir);

      const symlinkInfo = findSymlinkInfo(skillDir, skillsSymlinkDir);
      const category = symlinkInfo?.category || inferCategory(skillDir);

      const skill = extractSkillFromDir(skillDir, skillPath, repoRelativePath, lang, category);
      if (skill) {
        skills.push(skill);
        seen.add(skillDir);
      }
    }
  }

  // 3. Scan language-agnostic skills in .github/plugins/azure-skills/skills/
  // These are core/cross-language skills (e.g., the Microsoft Foundry orchestrator
  // and its 10 sub-skills like foundry-hosted-agents, foundry-toolboxes, etc.)
  // that aren't tied to a specific SDK language. Routed via the microsoft-foundry plugin.
  const azureSkillsDir = path.join(pluginsDir, "azure-skills", "skills");
  if (fs.existsSync(azureSkillsDir)) {
    for (const skillDir of fs.readdirSync(azureSkillsDir)) {
      if (seen.has(skillDir)) continue;

      const skillPath = path.join(azureSkillsDir, skillDir);
      if (!fs.statSync(skillPath).isDirectory()) continue;

      const repoRelativePath = `.github/plugins/azure-skills/skills/${skillDir}`;
      const lang: Skill["lang"] = "core";

      // Symlink info wins; otherwise infer from skill name (Foundry orchestrator/sub-skills
      // get "foundry"; other azure-skills entries get categorized by name pattern or fall to "general").
      const symlinkInfo = findSymlinkInfo(skillDir, skillsSymlinkDir);
      const category = symlinkInfo?.category || inferCategory(skillDir);

      const skill = extractSkillFromDir(skillDir, skillPath, repoRelativePath, lang, category);
      if (skill) {
        skills.push(skill);
        seen.add(skillDir);
      }
    }
  }

  return skills.sort((a, b) => a.name.localeCompare(b.name));
}

function main() {
  const skills = extractSkills();
  const outputPath = path.resolve(
    import.meta.dirname,
    "../src/data/skills.json"
  );

  fs.writeFileSync(outputPath, JSON.stringify(skills, null, 2));
  console.log(`Extracted ${skills.length} skills to ${outputPath}`);

  const langCounts: Record<string, number> = {};
  for (const skill of skills) {
    langCounts[skill.lang] = (langCounts[skill.lang] || 0) + 1;
  }
  console.log("Language distribution:", langCounts);
}

main();
