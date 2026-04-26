/**
 * Rivet Runner — called by Python via subprocess.
 * Reads client data from a temp JSON file, runs the Rivet graph,
 * and writes the generated letter to stdout.
 */

import { loadProjectFromFile, runGraph } from "@ironclad/rivet-node";
import { readFileSync } from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const GRAPH_ID = "YvuUKw6GH7rKzoZvTtSTC";
const PROJECT_PATH = path.resolve(__dirname, "../../Enter Challenge.rivet-project");

async function main() {
  const tmpFilePath = process.argv[2];
  if (!tmpFilePath) {
    process.stderr.write("Error: input file path not provided.\n");
    process.exit(1);
  }

  if (!process.env.OPENAI_API_KEY) {
    process.stderr.write("Error: OPENAI_API_KEY not set. Add it to web-app/backend/.env\n");
    process.exit(1);
  }

  const inputData = JSON.parse(readFileSync(tmpFilePath, "utf8"));

  const inputs = {};
  for (const [key, value] of Object.entries(inputData)) {
    inputs[key] = { type: "string", value };
  }

  const project = await loadProjectFromFile(PROJECT_PATH);

  const outputs = await runGraph(project, {
    graph: GRAPH_ID,
    openAiKey: process.env.OPENAI_API_KEY,
    inputs,
  });

  // Try common output key names from the graph
  const letter =
    outputs?.response?.value ??
    outputs?.output?.value ??
    outputs?.letter?.value ??
    Object.values(outputs).find((v) => typeof v?.value === "string" && v.value.length > 100)?.value ??
    "";

  if (!letter) {
    process.stderr.write("Warning: no text output found in graph results.\n");
    process.stderr.write("Available output keys: " + JSON.stringify(Object.keys(outputs)) + "\n");
  }

  // Write to output file (UTF-8) to avoid Windows stdout encoding issues
  const { writeFileSync } = await import("fs");
  const outputPath = process.argv[3];
  writeFileSync(outputPath, letter, "utf8");
}

main().catch((err) => {
  process.stderr.write("Fatal error: " + err.message + "\n");
  process.exit(1);
});