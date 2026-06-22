import { strict as assert } from "node:assert";
import { readFileSync } from "node:fs";
import { readdirSync } from "node:fs";
import { join } from "node:path";
import { test } from "node:test";

const repoRoot = join(process.cwd());
const schemaPath = join(repoRoot, "frontend", "src", "visual-registry", "atlasVisualObjects.schema.json");
const registryPath = join(repoRoot, "frontend", "src", "visual-registry", "atlasVisualObjects.json");
const schemaDocPath = join(repoRoot, "docs", "Brand", "visual-governance", "ATLAS_VISUAL_OBJECT_REGISTRY_SCHEMA.md");

const schema = JSON.parse(readFileSync(schemaPath, "utf8")) as any;
const registry = JSON.parse(readFileSync(registryPath, "utf8")) as any;
const schemaDoc = readFileSync(schemaDocPath, "utf8");

const allowedAxisValues = {
  size: new Set(["compact", "standard", "workspace"]),
  density: new Set(["compact", "comfortable", "expanded"]),
  tier: new Set(["relevant", "emerging", "neutral", "warning"]),
  motion: new Set(["static", "periodic_hold", "continuous_sweep"]),
  state: new Set(["default", "hover", "selected", "loading", "empty", "disabled"]),
  surface: new Set(["dark_panel", "shell_panel", "modal_panel"]),
  emphasis: new Set(["low", "medium", "high"]),
} as const;

const requiredObjectFields = [
  "object_id",
  "schema_version",
  "status",
  "semantic_role",
  "variant_axes",
  "token_bindings",
  "acceptance_criteria",
  "implementation_mapping",
];

const requiredVariantFields = [
  "variant_ref",
  "object_id",
  "axis_values",
  "token_bindings",
  "state_overrides",
  "acceptance_criteria_refs",
  "implementation_mapping",
];

const requiredInstanceFields = [
  "instance_id",
  "object_id",
  "variant_ref",
  "surface",
  "route",
  "state",
  "acceptance_criteria_refs",
  "implementation_mapping",
];

function walkFiles(rootDir: string): string[] {
  const entries = readdirSync(rootDir, { withFileTypes: true });
  const files: string[] = [];
  for (const entry of entries) {
    const fullPath = join(rootDir, entry.name);
    if (entry.isDirectory()) {
      files.push(...walkFiles(fullPath));
    } else {
      files.push(fullPath);
    }
  }
  return files;
}

function noRawValues(value: string) {
  assert.equal(/#[0-9a-fA-F]{3,8}\b/.test(value), false, "raw hex values are forbidden");
  assert.equal(/\b\d+px\b/.test(value), false, "raw px values are forbidden");
  assert.equal(/\b\d+(\.\d+)?s\b/.test(value), false, "raw durations are forbidden");
}

function collectStringValues(value: unknown, out: string[] = []): string[] {
  if (typeof value === "string") {
    out.push(value);
    return out;
  }
  if (Array.isArray(value)) {
    for (const entry of value) {
      collectStringValues(entry, out);
    }
    return out;
  }
  if (value && typeof value === "object") {
    for (const entry of Object.values(value as Record<string, unknown>)) {
      collectStringValues(entry, out);
    }
  }
  return out;
}

test("schema doc describes the required registry structure", () => {
  assert.match(schemaDoc, /ATLAS Visual Object Registry Schema/);
  assert.match(schemaDoc, /radar_workspace/);
  assert.match(schemaDoc, /radar_sweep_mark/);
  assert.match(schemaDoc, /signal_card/);
});

test("registry schema is well-formed", () => {
  assert.equal(schema.$id.endsWith("atlasVisualObjects.schema.json"), true);
  assert.equal(schema.type, "object");
  assert.equal(schema.required.includes("objects"), true);
  assert.equal(schema.required.includes("variants"), true);
  assert.equal(schema.required.includes("screen_instances"), true);
});

test("registry has the three required objects", () => {
  assert.equal(registry.schema_version, "ATLAS_VISUAL_OBJECT_REGISTRY_V1");
  assert.equal(registry.registry_status, "candidate_registry_foundation");
  assert.deepEqual(
    registry.objects.map((entry: any) => entry.object_id).sort(),
    ["radar_sweep_mark", "radar_workspace", "signal_card"],
  );
});

test("every object has the required fields", () => {
  for (const object of registry.objects as any[]) {
    for (const field of requiredObjectFields) {
      assert.ok(Object.prototype.hasOwnProperty.call(object, field), `missing object field: ${field}`);
    }
    assert.equal(object.schema_version, "ATLAS_VISUAL_OBJECT_REGISTRY_V1");
    assert.equal(object.status, "candidate");
  }
});

test("every variant resolves to a registered object and only uses allowed axis values", () => {
  const objectIds = new Set((registry.objects as any[]).map((entry) => entry.object_id));
  for (const variant of registry.variants as any[]) {
    for (const field of requiredVariantFields) {
      assert.ok(Object.prototype.hasOwnProperty.call(variant, field), `missing variant field: ${field}`);
    }
    assert.ok(objectIds.has(variant.object_id), `unknown object_id: ${variant.object_id}`);
    for (const [axis, value] of Object.entries(variant.axis_values)) {
      assert.ok(allowedAxisValues[axis as keyof typeof allowedAxisValues].has(String(value)), `unknown axis value for ${axis}: ${String(value)}`);
    }
  }
});

test("every screen instance resolves to a registered object and variant", () => {
  const objectIds = new Set((registry.objects as any[]).map((entry) => entry.object_id));
  const variantRefs = new Set((registry.variants as any[]).map((entry) => entry.variant_ref));
  for (const instance of registry.screen_instances as any[]) {
    for (const field of requiredInstanceFields) {
      assert.ok(Object.prototype.hasOwnProperty.call(instance, field), `missing instance field: ${field}`);
    }
    assert.ok(objectIds.has(instance.object_id), `unknown instance object_id: ${instance.object_id}`);
    assert.ok(variantRefs.has(instance.variant_ref), `unknown variant_ref: ${instance.variant_ref}`);
  }
});

test("acceptance references resolve", () => {
  const criteriaIds = new Set<string>();
  for (const object of registry.objects as any[]) {
    for (const criterion of object.acceptance_criteria as any[]) {
      criteriaIds.add(criterion.id);
    }
  }

  for (const variant of registry.variants as any[]) {
    for (const ref of variant.acceptance_criteria_refs as string[]) {
      assert.ok(criteriaIds.has(ref), `unresolved acceptance criteria ref: ${ref}`);
    }
  }

  for (const instance of registry.screen_instances as any[]) {
    for (const ref of instance.acceptance_criteria_refs as string[]) {
      assert.ok(criteriaIds.has(ref), `unresolved instance acceptance criteria ref: ${ref}`);
    }
  }
});

test("no raw hex colors, px values, or durations appear in the registry data", () => {
  for (const stringValue of collectStringValues(registry)) {
    noRawValues(stringValue);
  }
});

test("the registry stays out of live render files in this first E3", () => {
  const renderRoots = [
    join(repoRoot, "frontend", "src", "shell"),
    join(repoRoot, "frontend", "src", "workspaces"),
  ];
  for (const rootDir of renderRoots) {
    for (const filePath of walkFiles(rootDir)) {
      const contents = readFileSync(filePath, "utf8");
      assert.equal(
        /visual-registry/i.test(contents),
        false,
        `visual registry must not be imported by existing render files in the first E3: ${filePath}`,
      );
    }
  }
});

test("unknown states and variants are rejected by the symbolic vocabulary", () => {
  assert.equal(allowedAxisValues.state.has("unknown-state"), false);
  assert.equal(allowedAxisValues.motion.has("unknown-motion"), false);
  assert.equal(
    (registry.variants as any[]).some((variant) => variant.variant_ref === "unknown.variant.ref"),
    false,
  );
});
