import { build } from "esbuild";

await build({
  entryPoints: ["frontend/src/index.ts"],
  outfile: "custom_components/ha_drawio_editor/static/ha-drawio-editor.js",
  bundle: true,
  format: "esm",
  target: "es2022",
  minify: false,
  sourcemap: false,
  logLevel: "info",
});

