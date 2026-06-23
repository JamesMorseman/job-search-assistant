declare module "node:assert" {
  export const strict: {
    equal(actual: unknown, expected: unknown, message?: string): void;
    deepEqual(actual: unknown, expected: unknown, message?: string): void;
    ok(value: unknown, message?: string): void;
    match(actual: string, regexp: RegExp, message?: string): void;
  };
}

declare module "node:fs" {
  export interface Dirent {
    name: string;
    isDirectory(): boolean;
  }

  export function readFileSync(path: string, options: { encoding: "utf8" } | "utf8"): string;
  export function readFileSync(path: string, options?: string): string;
  export function readdirSync(path: string, options: { withFileTypes: true }): Dirent[];
  export function readdirSync(path: string, options?: string): string[];
}

declare module "node:path" {
  export function join(...parts: string[]): string;
}

declare module "node:test" {
  export function test(name: string, fn: () => void | Promise<void>): void;
}

declare const process: {
  cwd(): string;
};
