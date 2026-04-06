"""Constants for the Draw.io Editor integration."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "ha_drawio_editor"
ENTRY_TITLE: Final = "Draw.io Editor"
INTEGRATION_VERSION: Final = "0.1.0"

CONF_STORAGE_PATH: Final = "storage_path"
CONF_PANEL_URL_PATH: Final = "panel_url_path"
CONF_SIDEBAR_TITLE: Final = "sidebar_title"
CONF_SIDEBAR_ICON: Final = "sidebar_icon"
CONF_EDITOR_URL: Final = "editor_url"

OPT_ENABLE_PANEL: Final = "enable_panel"
OPT_ENABLE_OPEN_FILE: Final = "enable_open_file"
OPT_ENABLE_QUERY_OPEN: Final = "enable_query_open"
OPT_ENABLE_SAVE: Final = "enable_save"
OPT_ENABLE_PNG_EXPORT: Final = "enable_png_export"

DEFAULT_STORAGE_PATH: Final = "drawio"
DEFAULT_PANEL_URL_PATH: Final = "ha-drawio-editor"
DEFAULT_SIDEBAR_TITLE: Final = "Draw.io"
DEFAULT_SIDEBAR_ICON: Final = "mdi:vector-polyline-edit"
DEFAULT_EDITOR_URL: Final = "https://embed.diagrams.net/?embed=1&proto=json&spin=1&libraries=1"

DEFAULT_OPTIONS: Final = {
    OPT_ENABLE_PANEL: False,
    OPT_ENABLE_OPEN_FILE: False,
    OPT_ENABLE_QUERY_OPEN: False,
    OPT_ENABLE_SAVE: False,
    OPT_ENABLE_PNG_EXPORT: False,
}

ALLOWED_DIAGRAM_SUFFIXES: Final = frozenset({".drawio", ".xml"})

WEBCOMPONENT_NAME: Final = "ha-drawio-editor-panel"
STATIC_URL_BASE: Final = f"/api/{DOMAIN}/static"
STATIC_MODULE_FILENAME: Final = "ha-drawio-editor.js"

DATA_ACTIVE_ENTRY_ID: Final = f"{DOMAIN}_active_entry_id"
DATA_STATIC_REGISTERED: Final = f"{DOMAIN}_static_registered"
DATA_WEBSOCKET_REGISTERED: Final = f"{DOMAIN}_websocket_registered"

WS_TYPE_GET_CONFIG: Final = f"{DOMAIN}/get_config"
WS_TYPE_LOAD_DIAGRAM: Final = f"{DOMAIN}/load_diagram"
WS_TYPE_SAVE_DIAGRAM: Final = f"{DOMAIN}/save_diagram"

PNG_EXPORT_SCOPE_CURRENT_PAGE: Final = "current_page"

BLANK_DIAGRAM_XML: Final = """<mxfile host="app.diagrams.net" agent="ha-drawio-editor" version="26.0.11" type="device"><diagram id="blank-page" name="Page-1"><mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0"><root><mxCell id="0" /><mxCell id="1" parent="0" /></root></mxGraphModel></diagram></mxfile>"""

