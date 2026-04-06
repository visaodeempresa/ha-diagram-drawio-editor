export interface HomeAssistant {
  language: string;
  callWS<T>(message: Record<string, unknown>): Promise<T>;
}

export interface PanelInfo {
  title?: string | null;
}

export interface FeatureFlags {
  enable_panel: boolean;
  enable_open_file: boolean;
  enable_query_open: boolean;
  enable_save: boolean;
  enable_png_export: boolean;
}

export interface RuntimeConfig {
  domain: string;
  editor_url: string;
  editor_origin: string;
  panel_url_path: string;
  sidebar_title: string;
  sidebar_icon: string;
  storage_path: string;
  allowed_extensions: string[];
  feature_flags: FeatureFlags;
  png_export: {
    scope: "current_page";
    transparent: boolean;
    scale: number;
  };
}

export interface DiagramPayload {
  path: string;
  xml: string;
  png_path: string;
  png_exists: boolean;
}

export interface SavePayload {
  path: string;
  png_path: string;
  png_written: boolean;
}

export interface DrawioSaveEvent {
  event: "save";
  xml: string;
  exit?: boolean;
}

export interface DrawioExportEvent {
  event: "export";
  format: string;
  data: string;
}

export interface DrawioMessage {
  event?: string;
  action?: string;
  xml?: string;
  href?: string;
  target?: string;
  modified?: boolean;
  exit?: boolean;
  data?: string;
  config?: Record<string, unknown>;
  format?: string;
}

