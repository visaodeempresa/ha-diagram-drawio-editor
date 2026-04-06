# Architecture

## Goal

This project embeds the diagrams.net editor inside a Home Assistant custom panel and keeps the file operations inside Home Assistant. When save is enabled, the integration stores the `.drawio` XML and can also write a sibling `.png` file with the same basename.

## Components

### Home Assistant custom integration

- Registers a config entry and options flow.
- Owns the rollout feature flags.
- Serves the compiled frontend bundle as a static module.
- Registers the custom panel.
- Exposes authenticated WebSocket commands for runtime config, diagram load, and diagram save.
- Validates that all diagram paths stay under the configured storage root.

### TypeScript frontend panel

- Runs as a Home Assistant custom panel web component.
- Embeds `https://embed.diagrams.net` or a user-supplied compatible editor URL in an iframe.
- Implements the diagrams.net JSON protocol.
- Loads a `.drawio` file from Home Assistant when open is enabled.
- Requests a PNG export from the editor before persisting the save when PNG export is enabled.

## Rollout model

The repository is intentionally built around isolated rollout flags:

- `enable_panel`
- `enable_open_file`
- `enable_query_open`
- `enable_save`
- `enable_png_export`

Recommended progression:

1. Enable only `enable_panel` to validate panel rendering.
2. Enable `enable_open_file` and `enable_query_open` to open files from Lovelace buttons.
3. Enable `enable_save`.
4. Enable `enable_png_export`.

## Save path and PNG behavior

- The storage root is relative to the Home Assistant config directory.
- The diagram path must stay inside that root.
- Supported diagram extensions are `.drawio` and `.xml`.
- The sibling PNG path is generated with `Path.with_suffix(".png")`.
- The frontend currently exports the current page to one PNG because the requirement calls for one sibling PNG per diagram path.

## Security model

- The custom panel is registered as admin-only.
- The WebSocket API is admin-only.
- Paths are normalized and traversal outside the storage root is rejected.
- The frontend only accepts postMessage traffic from the configured editor origin.

## Known extension points

- Self-hosted diagrams.net can be enabled by changing the editor URL during setup.
- Multi-page export rules can be extended in the frontend export request.
- Additional file pickers or entity-driven entry points can be layered on top of the existing query-string open flow.

