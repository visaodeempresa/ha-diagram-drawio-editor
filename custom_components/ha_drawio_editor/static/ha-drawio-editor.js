// frontend/src/api.ts
var DOMAIN = "ha_drawio_editor";
var getRuntimeConfig = (hass) => hass.callWS({
  type: `${DOMAIN}/get_config`
});
var loadDiagram = (hass, path) => hass.callWS({
  type: `${DOMAIN}/load_diagram`,
  path
});
var saveDiagram = (hass, path, xml, pngDataUri) => hass.callWS({
  type: `${DOMAIN}/save_diagram`,
  path,
  xml,
  png_data_uri: pngDataUri
});

// frontend/src/index.ts
var BLANK_DIAGRAM_XML = '<mxfile host="app.diagrams.net" agent="ha-drawio-editor" version="26.0.11" type="device"><diagram id="blank-page" name="Page-1"><mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0"><root><mxCell id="0" /><mxCell id="1" parent="0" /></root></mxGraphModel></diagram></mxfile>';
var HaDrawioEditorPanel = class extends HTMLElement {
  _hass;
  _panel;
  runtimeConfig;
  initializing = false;
  currentPath = "";
  pendingSave;
  frameElement;
  noticeElement;
  statusElement;
  pathInputElement;
  openButtonElement;
  flagListElement;
  titleElement;
  set hass(value) {
    this._hass = value;
    void this.bootstrap();
  }
  get hass() {
    return this._hass;
  }
  set panel(value) {
    this._panel = value;
    this.updateTitle();
  }
  get panel() {
    return this._panel;
  }
  connectedCallback() {
    if (!this.shadowRoot) {
      this.attachShadow({ mode: "open" });
      this.renderShell();
    }
    window.addEventListener("message", this.handleWindowMessage);
    void this.bootstrap();
  }
  disconnectedCallback() {
    window.removeEventListener("message", this.handleWindowMessage);
  }
  renderShell() {
    if (!this.shadowRoot) {
      return;
    }
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          height: 100%;
          color: var(--primary-text-color);
          background:
            radial-gradient(circle at top right, rgba(255, 168, 0, 0.10), transparent 28%),
            radial-gradient(circle at bottom left, rgba(3, 169, 244, 0.12), transparent 30%),
            var(--primary-background-color);
        }

        .shell {
          display: grid;
          grid-template-rows: auto auto 1fr;
          gap: 12px;
          height: 100%;
          padding: 16px;
          box-sizing: border-box;
        }

        .toolbar,
        .notice,
        .status {
          border-radius: 16px;
          border: 1px solid rgba(255, 255, 255, 0.08);
          backdrop-filter: blur(12px);
          background: color-mix(in srgb, var(--card-background-color) 88%, transparent);
          box-shadow: 0 12px 30px rgba(0, 0, 0, 0.10);
        }

        .toolbar {
          display: grid;
          gap: 12px;
          padding: 16px;
        }

        .toolbar-header {
          display: flex;
          justify-content: space-between;
          gap: 12px;
          align-items: center;
          flex-wrap: wrap;
        }

        .title {
          font-size: 1.1rem;
          font-weight: 700;
          letter-spacing: 0.02em;
        }

        .subtitle {
          color: var(--secondary-text-color);
          font-size: 0.92rem;
        }

        .flags {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
        }

        .flag {
          padding: 6px 10px;
          border-radius: 999px;
          font-size: 0.78rem;
          border: 1px solid rgba(255, 255, 255, 0.08);
          background: rgba(0, 0, 0, 0.12);
        }

        .flag.enabled {
          border-color: rgba(255, 152, 0, 0.35);
          background: rgba(255, 152, 0, 0.16);
        }

        .path-row {
          display: grid;
          grid-template-columns: 1fr auto;
          gap: 12px;
          align-items: end;
        }

        label {
          display: grid;
          gap: 6px;
          font-size: 0.9rem;
          color: var(--secondary-text-color);
        }

        input {
          width: 100%;
          padding: 12px 14px;
          border-radius: 12px;
          border: 1px solid rgba(255, 255, 255, 0.10);
          background: color-mix(in srgb, var(--primary-background-color) 72%, transparent);
          color: var(--primary-text-color);
          font: inherit;
          box-sizing: border-box;
        }

        button {
          min-height: 44px;
          padding: 0 18px;
          border: 0;
          border-radius: 12px;
          font: inherit;
          font-weight: 700;
          color: white;
          background: linear-gradient(135deg, #ef6c00, #fb8c00);
          cursor: pointer;
        }

        button[disabled] {
          cursor: not-allowed;
          opacity: 0.55;
        }

        .notice,
        .status {
          padding: 12px 14px;
          font-size: 0.9rem;
        }

        .notice[hidden],
        .status[hidden] {
          display: none;
        }

        .notice.error {
          color: #ffccbc;
          border-color: rgba(244, 67, 54, 0.35);
          background: rgba(183, 28, 28, 0.18);
        }

        .notice.info {
          color: var(--primary-text-color);
        }

        .status {
          color: var(--secondary-text-color);
        }

        .frame-wrap {
          min-height: 0;
          border-radius: 22px;
          overflow: hidden;
          border: 1px solid rgba(255, 255, 255, 0.08);
          background: color-mix(in srgb, var(--card-background-color) 82%, transparent);
          box-shadow: 0 18px 36px rgba(0, 0, 0, 0.14);
        }

        iframe {
          display: block;
          width: 100%;
          height: 100%;
          min-height: 540px;
          border: 0;
          background: white;
        }

        @media (max-width: 800px) {
          .path-row {
            grid-template-columns: 1fr;
          }

          iframe {
            min-height: 460px;
          }
        }
      </style>
      <div class="shell">
        <div class="toolbar">
          <div class="toolbar-header">
            <div>
              <div class="title">Draw.io Editor</div>
              <div class="subtitle">Loading configuration\u2026</div>
            </div>
            <div class="flags"></div>
          </div>
          <div class="path-row">
            <label>
              <span>Relative diagram path</span>
              <input id="path-input" type="text" placeholder="floorplans/main.drawio" />
            </label>
            <button id="open-button" type="button">Open</button>
          </div>
        </div>
        <div class="notice info" id="notice" hidden></div>
        <div class="status" id="status" hidden></div>
        <div class="frame-wrap">
          <iframe
            id="editor-frame"
            referrerpolicy="strict-origin-when-cross-origin"
            sandbox="allow-downloads allow-forms allow-popups allow-popups-to-escape-sandbox allow-same-origin allow-scripts"
            title="Draw.io Editor"
          ></iframe>
        </div>
      </div>
    `;
    this.frameElement = this.shadowRoot.querySelector("#editor-frame") ?? void 0;
    this.noticeElement = this.shadowRoot.querySelector("#notice") ?? void 0;
    this.statusElement = this.shadowRoot.querySelector("#status") ?? void 0;
    this.pathInputElement = this.shadowRoot.querySelector("#path-input") ?? void 0;
    this.openButtonElement = this.shadowRoot.querySelector("#open-button") ?? void 0;
    this.flagListElement = this.shadowRoot.querySelector(".flags") ?? void 0;
    this.titleElement = this.shadowRoot.querySelector(".title") ?? void 0;
    this.openButtonElement?.addEventListener("click", () => {
      void this.handleOpenClick();
    });
    this.pathInputElement?.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        event.preventDefault();
        void this.handleOpenClick();
      }
    });
  }
  async bootstrap() {
    if (!this.isConnected || !this._hass || this.initializing) {
      return;
    }
    this.initializing = true;
    try {
      this.runtimeConfig = await getRuntimeConfig(this._hass);
      this.currentPath = this.resolveInitialPath();
      if (this.pathInputElement) {
        this.pathInputElement.value = this.currentPath;
      }
      if (this.frameElement && this.frameElement.src !== this.runtimeConfig.editor_url) {
        this.frameElement.src = this.runtimeConfig.editor_url;
      }
      this.updateTitle();
      this.updateFeatureFlags();
      this.updateControls();
      if (!this.runtimeConfig.feature_flags.enable_panel) {
        this.showNotice(
          "The panel feature flag is disabled. Enable it in the integration options to expose the panel.",
          "info"
        );
      } else {
        this.showNotice("", "info", true);
      }
    } catch (error) {
      this.showNotice(this.errorMessage(error), "error");
    } finally {
      this.initializing = false;
    }
  }
  updateControls() {
    if (!this.runtimeConfig || !this.pathInputElement || !this.openButtonElement) {
      return;
    }
    const canOpen = this.runtimeConfig.feature_flags.enable_open_file;
    this.pathInputElement.disabled = !canOpen;
    this.openButtonElement.disabled = !canOpen;
    const subtitle = this.shadowRoot?.querySelector(".subtitle");
    if (subtitle) {
      subtitle.textContent = `Storage root: ${this.runtimeConfig.storage_path}`;
    }
  }
  updateFeatureFlags() {
    if (!this.runtimeConfig || !this.flagListElement) {
      return;
    }
    const flagLabels = [
      ["enable_panel", "Panel"],
      ["enable_open_file", "Open"],
      ["enable_query_open", "URL open"],
      ["enable_save", "Save"],
      ["enable_png_export", "PNG export"]
    ];
    this.flagListElement.innerHTML = flagLabels.map(([key, label]) => {
      const enabled = this.runtimeConfig?.feature_flags[key] ?? false;
      return `<span class="flag ${enabled ? "enabled" : ""}">${label}: ${enabled ? "on" : "off"}</span>`;
    }).join("");
  }
  updateTitle() {
    if (!this.titleElement) {
      return;
    }
    const configuredTitle = this.runtimeConfig?.sidebar_title ?? this._panel?.title ?? "Draw.io Editor";
    this.titleElement.textContent = configuredTitle;
  }
  resolveInitialPath() {
    if (!this.runtimeConfig) {
      return "";
    }
    const params = new URL(window.location.href).searchParams;
    const requestedPath = params.get("path")?.trim() ?? "";
    if (!requestedPath) {
      return "";
    }
    if (!this.runtimeConfig.feature_flags.enable_query_open) {
      this.showNotice(
        "A path was provided in the URL, but query-string open is disabled by the current feature rollout.",
        "info"
      );
      return "";
    }
    return requestedPath;
  }
  handleWindowMessage = (event) => {
    if (!this.runtimeConfig || event.origin !== this.runtimeConfig.editor_origin) {
      return;
    }
    const message = this.parseMessage(event.data);
    if (!message) {
      return;
    }
    switch (message.event) {
      case "configure":
        this.postToEditor({
          action: "configure",
          config: {}
        });
        return;
      case "init":
        void this.loadCurrentDiagram();
        return;
      case "save":
        void this.handleSaveEvent(message);
        return;
      case "export":
        void this.handleExportEvent(message);
        return;
      case "openLink":
        if (message.href) {
          window.open(message.href, message.target ?? "_blank", "noopener");
        }
        return;
      default:
        return;
    }
  };
  parseMessage(payload) {
    if (typeof payload === "string") {
      try {
        return JSON.parse(payload);
      } catch (_error) {
        return void 0;
      }
    }
    return payload;
  }
  async handleOpenClick() {
    if (!this.runtimeConfig || !this.pathInputElement) {
      return;
    }
    this.currentPath = this.pathInputElement.value.trim();
    await this.loadCurrentDiagram();
  }
  async loadCurrentDiagram() {
    if (!this.runtimeConfig) {
      return;
    }
    const filePath = this.currentPath.trim();
    const canOpen = this.runtimeConfig.feature_flags.enable_open_file;
    if (!canOpen || !filePath) {
      this.postLoadToEditor({
        xml: BLANK_DIAGRAM_XML,
        title: filePath || "New diagram"
      });
      this.showStatus("Blank canvas loaded.");
      return;
    }
    if (!this._hass) {
      return;
    }
    this.showStatus("Loading diagram\u2026");
    try {
      const payload = await loadDiagram(this._hass, filePath);
      this.currentPath = payload.path;
      if (this.pathInputElement) {
        this.pathInputElement.value = payload.path;
      }
      this.postLoadToEditor({
        xml: payload.xml,
        title: payload.path
      });
      this.showNotice("", "info", true);
      this.showStatus(`Loaded ${payload.path}`);
    } catch (error) {
      if (this.errorCode(error) === "not_found") {
        this.postLoadToEditor({
          xml: BLANK_DIAGRAM_XML,
          title: filePath
        });
        this.showNotice(
          `File "${filePath}" was not found. A blank canvas was loaded and saving will create the file.`,
          "info"
        );
        this.showStatus(`Prepared blank canvas for ${filePath}`);
        return;
      }
      this.showNotice(this.errorMessage(error), "error");
      this.showStatus("Diagram load failed.");
    }
  }
  async handleSaveEvent(message) {
    if (!this.runtimeConfig) {
      return;
    }
    if (!this.runtimeConfig.feature_flags.enable_save) {
      this.showNotice(
        "Save was requested by the editor, but the save feature flag is disabled.",
        "error"
      );
      this.postToEditor({
        action: "status",
        message: "Save is disabled by the current feature rollout."
      });
      return;
    }
    const targetPath = this.pathInputElement?.value.trim() || this.currentPath.trim();
    if (!targetPath) {
      this.showNotice("Set a relative file path before saving.", "error");
      this.postToEditor({
        action: "status",
        message: "Set a relative file path before saving."
      });
      return;
    }
    this.currentPath = targetPath;
    this.pendingSave = {
      xml: message.xml,
      exit: Boolean(message.exit)
    };
    if (this.runtimeConfig.feature_flags.enable_png_export) {
      this.showStatus("Generating PNG export\u2026");
      this.postToEditor({
        action: "export",
        format: "png",
        currentPage: true,
        transparent: this.runtimeConfig.png_export.transparent,
        scale: this.runtimeConfig.png_export.scale
      });
      return;
    }
    await this.persistSave(null);
  }
  async handleExportEvent(message) {
    if (!this.pendingSave) {
      return;
    }
    if (message.format !== "png" || !message.data) {
      this.showNotice("The editor returned an invalid PNG export.", "error");
      this.showStatus("PNG export failed.");
      this.pendingSave = void 0;
      return;
    }
    await this.persistSave(message.data);
  }
  async persistSave(pngDataUri) {
    if (!this._hass || !this.pendingSave) {
      return;
    }
    const targetPath = this.currentPath.trim();
    if (!targetPath) {
      this.showNotice("Set a relative file path before saving.", "error");
      this.pendingSave = void 0;
      return;
    }
    this.showStatus("Saving diagram\u2026");
    try {
      const result = await saveDiagram(
        this._hass,
        targetPath,
        this.pendingSave.xml,
        pngDataUri
      );
      this.postToEditor({
        action: "status",
        message: result.png_written ? `Saved ${result.path} and ${result.png_path}` : `Saved ${result.path}`,
        modified: false
      });
      this.showNotice("", "info", true);
      this.showStatus(
        result.png_written ? `Saved ${result.path} and generated ${result.png_path}` : `Saved ${result.path}`
      );
    } catch (error) {
      this.showNotice(this.errorMessage(error), "error");
      this.showStatus("Save failed.");
    } finally {
      this.pendingSave = void 0;
    }
  }
  postLoadToEditor(payload) {
    if (!this.runtimeConfig) {
      return;
    }
    this.postToEditor({
      action: "load",
      xml: payload.xml,
      title: payload.title,
      noSaveBtn: this.runtimeConfig.feature_flags.enable_save ? 0 : 1,
      saveAndExit: 0,
      noExitBtn: 1
    });
  }
  postToEditor(message) {
    if (!this.runtimeConfig || !this.frameElement?.contentWindow) {
      return;
    }
    this.frameElement.contentWindow.postMessage(
      JSON.stringify(message),
      this.runtimeConfig.editor_origin
    );
  }
  showNotice(message, kind, hidden = false) {
    if (!this.noticeElement) {
      return;
    }
    this.noticeElement.hidden = hidden || !message;
    this.noticeElement.textContent = message;
    this.noticeElement.className = `notice ${kind}`;
  }
  showStatus(message, hidden = false) {
    if (!this.statusElement) {
      return;
    }
    this.statusElement.hidden = hidden || !message;
    this.statusElement.textContent = message;
  }
  errorCode(error) {
    if (typeof error === "object" && error !== null && "code" in error) {
      const code = error.code;
      if (typeof code === "string") {
        return code;
      }
    }
    return void 0;
  }
  errorMessage(error) {
    if (typeof error === "object" && error !== null) {
      if ("message" in error && typeof error.message === "string") {
        return error.message;
      }
      if ("code" in error && typeof error.code === "string") {
        return error.code;
      }
    }
    if (error instanceof Error) {
      return error.message;
    }
    return "Unexpected error";
  }
};
customElements.define("ha-drawio-editor-panel", HaDrawioEditorPanel);
