import type {
  DiagramPayload,
  HomeAssistant,
  RuntimeConfig,
  SavePayload,
} from "./types";

const DOMAIN = "ha_drawio_editor";

export const getRuntimeConfig = (hass: HomeAssistant): Promise<RuntimeConfig> =>
  hass.callWS<RuntimeConfig>({
    type: `${DOMAIN}/get_config`,
  });

export const loadDiagram = (
  hass: HomeAssistant,
  path: string,
): Promise<DiagramPayload> =>
  hass.callWS<DiagramPayload>({
    type: `${DOMAIN}/load_diagram`,
    path,
  });

export const saveDiagram = (
  hass: HomeAssistant,
  path: string,
  xml: string,
  pngDataUri: string | null,
): Promise<SavePayload> =>
  hass.callWS<SavePayload>({
    type: `${DOMAIN}/save_diagram`,
    path,
    xml,
    png_data_uri: pngDataUri,
  });

