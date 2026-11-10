"""
Fase 2B - Generador corregido de visuals PBIR para Energy Demand Intelligence Dashboard.
Alineado estrictamente con las propiedades descubiertas del CLI powerbi-report-author.
Canvas: 1920 x 1080 FHD.
"""

import json
import os
import hashlib

# Ruta absoluta al directorio de visuals
REPO_ROOT = r"C:\Users\camil\Escritorio\energy_demand_intelligence_repo"
VISUALS_DIR = os.path.join(REPO_ROOT, r"powerbi\Energy_Demand_Intelligence.Report\definition\pages\fee72c677b8c7615b78a\visuals")
SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.9.0/schema.json"

os.makedirs(VISUALS_DIR, exist_ok=True)

def vid(seed: str) -> str:
    return hashlib.md5(seed.encode()).hexdigest()[:20]

def write_visual(name: str, visual_def: dict):
    path = os.path.join(VISUALS_DIR, name)
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, "visual.json"), "w", encoding="utf-8") as f:
        json.dump(visual_def, f, indent=2, ensure_ascii=False)

def measure_field(table: str, measure: str):
    return {
        "Measure": {
            "Expression": {"SourceRef": {"Entity": table}},
            "Property": measure
        }
    }

def column_field(table: str, column: str):
    return {
        "Column": {
            "Expression": {"SourceRef": {"Entity": table}},
            "Property": column
        }
    }

def proj(table: str, prop: str, is_measure: bool = True, qref: str = None):
    field = measure_field(table, prop) if is_measure else column_field(table, prop)
    return {
        "field": field,
        "queryRef": qref or f"{table}.{prop}",
        "nativeQueryRef": prop
    }

def lit(value):
    return {"expr": {"Literal": {"Value": value}}}

def color_solid(hex_color):
    return {"solid": {"color": {"expr": {"Literal": {"Value": f"'{hex_color}'"}}}}}

CARD_H = 97
CARD_VALUE_FS = 28
CARD_LABEL_FS = 14

# ─── 1. HEADER BACKGROUND (shape) ────────────────────────────────────────────
header_id = vid("header_bg")
write_visual(header_id, {
    "$schema": SCHEMA,
    "name": header_id,
    "position": {"x": 0, "y": 0, "z": 1000, "height": 60, "width": 1920, "tabOrder": 1000},
    "visual": {
        "visualType": "shape",
        "query": {"queryState": {}},
        "objects": {
            "outline": [{"properties": {
                "lineColor": color_solid("#0A2540"),
                "transparency": lit("0D"),
                "weight": lit("0D")
            }}],
            "fill": [{"properties": {
                "fillColor": color_solid("#0A2540"),
                "transparency": lit("0D")
            }}],
            "rotation": [{"properties": {
                "angle": lit("0D")
            }}],
            "shape": [{"properties": {
                "tileShape": lit("'rectangle'")
            }}]
        },
        "visualContainerObjects": {
            "padding": [{"properties": {
                "top": lit("0D"), "bottom": lit("0D"),
                "left": lit("0D"), "right": lit("0D")
            }}]
        }
    }
})

# ─── 2. HEADER TITLE TEXTBOX ─────────────────────────────────────────────────
header_title_id = vid("header_title_txt")
write_visual(header_title_id, {
    "$schema": SCHEMA,
    "name": header_title_id,
    "position": {"x": 16, "y": 2, "z": 2000, "height": 56, "width": 900, "tabOrder": 2000},
    "visual": {
        "visualType": "textbox",
        "query": {"queryState": {}},
        "objects": {
            "general": [{"properties": {
                "paragraphs": lit(json.dumps([{
                    "textRuns": [
                        {
                            "value": "⚡  Demanda Eléctrica de Tétouan",
                            "textStyle": {
                                "fontWeight": "bold",
                                "fontSize": "18pt",
                                "color": "#FFFFFF",
                                "fontFamily": "Segoe UI"
                            }
                        },
                        {
                            "value": "   |   Pronóstico de demanda y detección de picos",
                            "textStyle": {
                                "fontSize": "12pt",
                                "color": "#BAE6FD",
                                "fontFamily": "Segoe UI"
                            }
                        }
                    ]
                }]))
            }}]
        },
        "visualContainerObjects": {
            "padding": [{"properties": {
                "top": lit("8D"), "bottom": lit("0D"),
                "left": lit("8D"), "right": lit("8D")
            }}]
        }
    }
})

# ─── 3. HEADER METADATA (right side) ─────────────────────────────────────────
header_meta_id = vid("header_meta_txt")
write_visual(header_meta_id, {
    "$schema": SCHEMA,
    "name": header_meta_id,
    "position": {"x": 920, "y": 2, "z": 2000, "height": 56, "width": 1000, "tabOrder": 2001},
    "visual": {
        "visualType": "textbox",
        "query": {"queryState": {}},
        "objects": {
            "general": [{"properties": {
                "paragraphs": lit(json.dumps([{
                    "textRuns": [
                        {
                            "value": "📅  Última actualización: 30 dic 2017 · 23:00     |     🤖  Pronóstico: AutoARIMA + Estacional     |     📊  Picos: Regresión Logística     |     ⚠ Prototipo Histórico 2017",
                            "textStyle": {
                                "fontSize": "11pt",
                                "color": "#BAE6FD",
                                "fontFamily": "Segoe UI"
                            }
                        }
                    ],
                    "horizontalTextAlignment": "Right"
                }]))
            }}]
        },
        "visualContainerObjects": {
            "padding": [{"properties": {
                "top": lit("8D"), "bottom": lit("0D"),
                "left": lit("8D"), "right": lit("16D")
            }}]
        }
    }
})

# ─── 4. LEFT RAIL BACKGROUND ──────────────────────────────────────────────────
left_rail_bg_id = vid("left_rail_bg")
write_visual(left_rail_bg_id, {
    "$schema": SCHEMA,
    "name": left_rail_bg_id,
    "position": {"x": 0, "y": 60, "z": 500, "height": 1020, "width": 260, "tabOrder": 500},
    "visual": {
        "visualType": "shape",
        "query": {"queryState": {}},
        "objects": {
            "outline": [{"properties": {
                "lineColor": color_solid("#E2E8F0"),
                "transparency": lit("0D"),
                "weight": lit("1D")
            }}],
            "fill": [{"properties": {
                "fillColor": color_solid("#FFFFFF"),
                "transparency": lit("0D")
            }}],
            "rotation": [{"properties": {"angle": lit("0D")}}],
            "shape": [{"properties": {"tileShape": lit("'rectangle'")}}]
        },
        "visualContainerObjects": {
            "padding": [{"properties": {
                "top": lit("0D"), "bottom": lit("0D"),
                "left": lit("0D"), "right": lit("0D")
            }}]
        }
    }
})

# ─── 5. LEFT RAIL LABEL ───────────────────────────────────────────────────────
left_label_id = vid("left_rail_label")
write_visual(left_label_id, {
    "$schema": SCHEMA,
    "name": left_label_id,
    "position": {"x": 8, "y": 68, "z": 2000, "height": 32, "width": 244, "tabOrder": 2002},
    "visual": {
        "visualType": "textbox",
        "query": {"queryState": {}},
        "objects": {
            "general": [{"properties": {
                "paragraphs": lit(json.dumps([{
                    "textRuns": [{
                        "value": "🗺  Red de Distribución",
                        "textStyle": {
                            "fontWeight": "bold",
                            "fontSize": "11pt",
                            "color": "#0A2540",
                            "fontFamily": "Segoe UI"
                        }
                    }]
                }]))
            }}]
        },
        "visualContainerObjects": {
            "padding": [{"properties": {
                "top": lit("4D"), "bottom": lit("0D"),
                "left": lit("8D"), "right": lit("8D")
            }}]
        }
    }
})

# ─── 6. REAL TÉTOUAN AERIAL MAP VISUAL ────────────────────────────────────────
map_card_id = vid("tetouan_real_map")
write_visual(map_card_id, {
    "$schema": SCHEMA,
    "name": map_card_id,
    "position": {"x": 8, "y": 105, "z": 2000, "height": 200, "width": 244, "tabOrder": 2003},
    "visual": {
        "visualType": "map",
        "query": {
            "queryState": {
                "Location": {
                    "projections": [proj("Dim_Zona", "zona_alias", is_measure=False)]
                },
                "Latitude": {
                    "projections": [proj("Dim_Zona", "latitud", is_measure=False)]
                },
                "Longitude": {
                    "projections": [proj("Dim_Zona", "longitud", is_measure=False)]
                }
            }
        },
        "objects": {
            "mapStyles": [{"properties": {
                "mapTheme": lit("'Aerial'")
            }}],
            "bubbles": [{"properties": {
                "markerSize": lit("25D")
            }}],
            "controls": [{"properties": {
                "showZoomButtons": lit("false")
            }}]
        },
        "visualContainerObjects": {
            "background": [{"properties": {
                "show": lit("true"),
                "color": color_solid("#FFFFFF"),
                "transparency": lit("0D")
            }}],
            "border": [{"properties": {
                "show": lit("true"),
                "color": color_solid("#E2E8F0"),
                "radius": lit("6D")
            }}],
            "padding": [{"properties": {
                "top": lit("0D"), "bottom": lit("0D"),
                "left": lit("0D"), "right": lit("0D")
            }}]
        }
    }
})

# ─── 7. ZONE SLICER (below map in left rail) ──────────────────────────────────
zone_slicer_id = vid("zone_slicer_main")
write_visual(zone_slicer_id, {
    "$schema": SCHEMA,
    "name": zone_slicer_id,
    "position": {"x": 8, "y": 315, "z": 2000, "height": 400, "width": 244, "tabOrder": 2005},
    "visual": {
        "visualType": "slicer",
        "query": {
            "queryState": {
                "Values": {
                    "projections": [proj("Dim_Zona", "zona_nombre", is_measure=False)]
                }
            }
        },
        "objects": {
            "data": [{"properties": {
                "mode": lit("'Basic'")
            }}],
            "header": [{"properties": {
                "show": lit("true"),
                "text": lit("'Selección de zona'"),
                "textSize": lit("10D"),
                "fontColor": color_solid("#0A2540")
            }}],
            "items": [{"properties": {
                "fontColor": color_solid("#0A2540"),
                "textSize": lit("11D"),
                "background": color_solid("#F8FAFC")
            }}],
            "selection": [{"properties": {
                "selectAllCheckboxEnabled": lit("true"),
                "singleSelect": lit("false")
            }}]
        },
        "visualContainerObjects": {
            "padding": [{"properties": {
                "top": lit("8D"), "bottom": lit("8D"),
                "left": lit("8D"), "right": lit("8D")
            }}]
        }
    }
})

# ─── 8. NARRATIVE BANNER ─────────────────────────────────────────────────────
narrative_id = vid("narrative_banner")
write_visual(narrative_id, {
    "$schema": SCHEMA,
    "name": narrative_id,
    "position": {"x": 276, "y": 60, "z": 2000, "height": 96, "width": 1240, "tabOrder": 2005},
    "visual": {
        "visualType": "cardVisual",
        "query": {
            "queryState": {
                "Data": {
                    "projections": [proj("_Medidas", "Resumen Perspectiva Dinamica")]
                }
            }
        },
        "objects": {
            "value": [{"properties": {
                "fontSize": lit("12D"),
                "fontColor": color_solid("#0A2540"),
                "fontFamily": lit("'Segoe UI'")
            }, "selector": {"id": "default"}}],
            "label": [{"properties": {
                "show": lit("false")
            }, "selector": {"id": "default"}}],
            "padding": [{"properties": {"paddingUniform": lit("8D")}, "selector": {"id": "default"}}],
            "layout": [{"properties": {"paddingUniform": lit("0D")}, "selector": {"id": "default"}}]
        },
        "visualContainerObjects": {
            "background": [{"properties": {
                "show": lit("true"),
                "color": color_solid("#FFFFFF"),
                "transparency": lit("0D")
            }}],
            "border": [{"properties": {
                "show": lit("true"),
                "color": color_solid("#E2E8F0"),
                "radius": lit("4D")
            }}],
            "padding": [{"properties": {
                "top": lit("8D"), "bottom": lit("8D"),
                "left": lit("12D"), "right": lit("12D")
            }}],
            "title": [{"properties": {
                "show": lit("true"),
                "text": lit("'💡 Perspectiva de demanda – Próximas 24 horas'"),
                "fontSize": lit("11D"),
                "fontColor": color_solid("#0052CC"),
                "fontFamily": lit("'Segoe UI Semibold'")
            }}]
        }
    }
})

# ─── 9. ALERT BADGE ──────────────────────────────────────────────────────────
alert_id = vid("alert_badge_card")
write_visual(alert_id, {
    "$schema": SCHEMA,
    "name": alert_id,
    "position": {"x": 1532, "y": 60, "z": 2000, "height": 96, "width": 388, "tabOrder": 2006},
    "visual": {
        "visualType": "cardVisual",
        "query": {
            "queryState": {
                "Data": {
                    "projections": [proj("_Medidas", "Alerta Estado Operativo")]
                }
            }
        },
        "objects": {
            "value": [{"properties": {
                "fontSize": lit("11D"),
                "fontColor": color_solid("#D97706"),
                "fontFamily": lit("'Segoe UI Semibold'")
            }, "selector": {"id": "default"}}],
            "label": [{"properties": {"show": lit("false")}, "selector": {"id": "default"}}],
            "padding": [{"properties": {"paddingUniform": lit("8D")}, "selector": {"id": "default"}}],
            "layout": [{"properties": {"paddingUniform": lit("0D")}, "selector": {"id": "default"}}]
        },
        "visualContainerObjects": {
            "background": [{"properties": {
                "show": lit("true"),
                "color": color_solid("#FEF3C7"),
                "transparency": lit("0D")
            }}],
            "border": [{"properties": {
                "show": lit("true"),
                "color": color_solid("#D97706"),
                "radius": lit("4D")
            }}],
            "padding": [{"properties": {
                "top": lit("8D"), "bottom": lit("8D"),
                "left": lit("12D"), "right": lit("12D")
            }}],
            "title": [{"properties": {
                "show": lit("true"),
                "text": lit("'⚠ Atención'"),
                "fontSize": lit("11D"),
                "fontColor": color_solid("#92400E"),
                "fontFamily": lit("'Segoe UI Semibold'")
            }}]
        }
    }
})

# ─── 10. KPI STRIP — 4 cards (multi-value card) ───────────────────────────────
kpi_strip_id = vid("kpi_strip_4cards")
write_visual(kpi_strip_id, {
    "$schema": SCHEMA,
    "name": kpi_strip_id,
    "position": {"x": 276, "y": 172, "z": 2000, "height": CARD_H, "width": 1240, "tabOrder": 2007},
    "visual": {
        "visualType": "cardVisual",
        "query": {
            "queryState": {
                "Data": {
                    "projections": [
                        proj("_Medidas", "Demanda Media KPI Formato"),
                        proj("_Medidas", "Pico Estimado KPI Formato"),
                        proj("_Medidas", "Horas Demanda Elevada"),
                        proj("_Medidas", "Probabilidad Pico Horizonte")
                    ]
                }
            }
        },
        "objects": {
            "value": [{"properties": {
                "fontSize": lit(f"{CARD_VALUE_FS}D"),
                "fontColor": color_solid("#0A2540"),
                "fontFamily": lit("'Segoe UI Semibold'")
            }, "selector": {"id": "default"}}],
            "label": [{"properties": {
                "fontSize": lit(f"{CARD_LABEL_FS}D"),
                "fontColor": color_solid("#64748B"),
                "fontFamily": lit("'Segoe UI'")
            }, "selector": {"id": "default"}}],
            "padding": [{"properties": {"paddingUniform": lit("8D")}, "selector": {"id": "default"}}],
            "layout": [{"properties": {"paddingUniform": lit("0D")}, "selector": {"id": "default"}}]
        },
        "visualContainerObjects": {
            "background": [{"properties": {
                "show": lit("true"),
                "color": color_solid("#FFFFFF"),
                "transparency": lit("0D")
            }}],
            "border": [{"properties": {
                "show": lit("true"),
                "color": color_solid("#E2E8F0"),
                "radius": lit("4D")
            }}],
            "padding": [{"properties": {
                "top": lit("8D"), "bottom": lit("8D"),
                "left": lit("12D"), "right": lit("12D")
            }}],
            "spacing": [{"properties": {
                "customizeSpacing": lit("true"),
                "verticalSpacing": lit("2D")
            }, "selector": {"id": "default"}}]
        }
    }
})

# ─── 11. WEATHER CARD ─────────────────────────────────────────────────────────
weather_id = vid("weather_context_card")
write_visual(weather_id, {
    "$schema": SCHEMA,
    "name": weather_id,
    "position": {"x": 1532, "y": 172, "z": 2000, "height": CARD_H, "width": 388, "tabOrder": 2008},
    "visual": {
        "visualType": "cardVisual",
        "query": {
            "queryState": {
                "Data": {
                    "projections": [
                        proj("_Medidas", "Temperatura Promedio Contexto"),
                        proj("_Medidas", "Humedad Promedio Contexto"),
                        proj("_Medidas", "Viento Promedio Contexto")
                    ]
                }
            }
        },
        "objects": {
            "value": [{"properties": {
                "fontSize": lit("18D"),
                "fontColor": color_solid("#0A2540"),
                "fontFamily": lit("'Segoe UI Semibold'")
            }, "selector": {"id": "default"}}],
            "label": [{"properties": {
                "fontSize": lit("10D"),
                "fontColor": color_solid("#64748B"),
                "fontFamily": lit("'Segoe UI'")
            }, "selector": {"id": "default"}}],
            "padding": [{"properties": {"paddingUniform": lit("8D")}, "selector": {"id": "default"}}],
            "layout": [{"properties": {"paddingUniform": lit("0D")}, "selector": {"id": "default"}}]
        },
        "visualContainerObjects": {
            "background": [{"properties": {
                "show": lit("true"),
                "color": color_solid("#FFFFFF"),
                "transparency": lit("0D")
            }}],
            "border": [{"properties": {
                "show": lit("true"),
                "color": color_solid("#E2E8F0"),
                "radius": lit("4D")
            }}],
            "padding": [{"properties": {
                "top": lit("8D"), "bottom": lit("8D"),
                "left": lit("12D"), "right": lit("12D")
            }}],
            "title": [{"properties": {
                "show": lit("true"),
                "text": lit("'🌤 Condiciones observadas (Tétouan)'"),
                "fontSize": lit("10D"),
                "fontColor": color_solid("#0A2540"),
                "fontFamily": lit("'Segoe UI Semibold'")
            }}],
            "spacing": [{"properties": {
                "customizeSpacing": lit("true"),
                "verticalSpacing": lit("2D")
            }, "selector": {"id": "default"}}]
        }
    }
})

# ─── 12. HORIZON SLICER ───────────────────────────────────────────────────────
horiz_slicer_id = vid("horizonte_slicer")
write_visual(horiz_slicer_id, {
    "$schema": SCHEMA,
    "name": horiz_slicer_id,
    "position": {"x": 276, "y": 285, "z": 3000, "height": 44, "width": 320, "tabOrder": 3001},
    "visual": {
        "visualType": "slicer",
        "query": {
            "queryState": {
                "Values": {
                    "projections": [proj("Dim_Horizonte", "horizonte", is_measure=False)]
                }
            }
        },
        "objects": {
            "data": [{"properties": {
                "mode": lit("'Basic'")
            }}],
            "header": [{"properties": {
                "show": lit("true"),
                "text": lit("'Horizonte de pronóstico'"),
                "textSize": lit("10D"),
                "fontColor": color_solid("#0A2540")
            }}],
            "items": [{"properties": {
                "fontColor": color_solid("#0052CC"),
                "textSize": lit("10D"),
                "background": color_solid("#FFFFFF")
            }}],
            "selection": [{"properties": {
                "singleSelect": lit("true")
            }}]
        },
        "visualContainerObjects": {
            "background": [{"properties": {
                "show": lit("true"),
                "color": color_solid("#FFFFFF"),
                "transparency": lit("0D")
            }}],
            "border": [{"properties": {
                "show": lit("true"),
                "color": color_solid("#E2E8F0"),
                "radius": lit("4D")
            }}],
            "padding": [{"properties": {
                "top": lit("4D"), "bottom": lit("4D"),
                "left": lit("8D"), "right": lit("8D")
            }}]
        }
    }
})

# ─── 13. VENTANA HISTORICA SLICER ────────────────────────────────────────────
ventana_slicer_id = vid("ventana_historica_slicer")
write_visual(ventana_slicer_id, {
    "$schema": SCHEMA,
    "name": ventana_slicer_id,
    "position": {"x": 612, "y": 285, "z": 3000, "height": 44, "width": 480, "tabOrder": 3002},
    "visual": {
        "visualType": "slicer",
        "query": {
            "queryState": {
                "Values": {
                    "projections": [proj("Dim_Ventana_Historica", "ventana_nombre", is_measure=False)]
                }
            }
        },
        "objects": {
            "data": [{"properties": {
                "mode": lit("'Basic'")
            }}],
            "header": [{"properties": {
                "show": lit("true"),
                "text": lit("'Ventana histórica'"),
                "textSize": lit("10D"),
                "fontColor": color_solid("#0A2540")
            }}],
            "items": [{"properties": {
                "fontColor": color_solid("#0052CC"),
                "textSize": lit("10D"),
                "background": color_solid("#FFFFFF")
            }}],
            "selection": [{"properties": {
                "singleSelect": lit("true")
            }}]
        },
        "visualContainerObjects": {
            "background": [{"properties": {
                "show": lit("true"),
                "color": color_solid("#FFFFFF"),
                "transparency": lit("0D")
            }}],
            "border": [{"properties": {
                "show": lit("true"),
                "color": color_solid("#E2E8F0"),
                "radius": lit("4D")
            }}],
            "padding": [{"properties": {
                "top": lit("4D"), "bottom": lit("4D"),
                "left": lit("8D"), "right": lit("8D")
            }}]
        }
    }
})

# ─── 14. HERO LINE CHART ─────────────────────────────────────────────────────
hero_chart_id = vid("hero_line_chart_main")
write_visual(hero_chart_id, {
    "$schema": SCHEMA,
    "name": hero_chart_id,
    "position": {"x": 276, "y": 341, "z": 2000, "height": 404, "width": 1644, "tabOrder": 2009},
    "visual": {
        "visualType": "areaChart",
        "query": {
            "queryState": {
                "Category": {
                    "projections": [{
                        "field": column_field("Dim_Calendario", "datetime"),
                        "queryRef": "Dim_Calendario.datetime",
                        "nativeQueryRef": "datetime"
                    }]
                },
                "Y": {
                    "projections": [
                        proj("_Medidas", "Demanda Real Ventana"),
                        proj("_Medidas", "Demanda Pronosticada"),
                        proj("_Medidas", "Banda Inferior 80%"),
                        proj("_Medidas", "Banda Superior 80%"),
                        proj("_Medidas", "Umbral P95"),
                        proj("_Medidas", "Evento Pico Estimado")
                    ]
                }
            },
            "sortDefinition": {
                "sort": [{
                    "field": column_field("Dim_Calendario", "datetime"),
                    "direction": "Ascending"
                }],
                "isDefaultSort": False
            }
        },
        "objects": {
            "dataPoint": [
                {
                    "properties": {
                        "defaultColor": color_solid("#0D9488")
                    },
                    "selector": {
                        "metadata": "Demanda Real Ventana"
                    }
                },
                {
                    "properties": {
                        "defaultColor": color_solid("#1D4ED8")
                    },
                    "selector": {
                        "metadata": "Demanda Pronosticada"
                    }
                },
                {
                    "properties": {
                        "defaultColor": color_solid("#93C5FD")
                    },
                    "selector": {
                        "metadata": "Banda Inferior 80%"
                    }
                },
                {
                    "properties": {
                        "defaultColor": color_solid("#93C5FD")
                    },
                    "selector": {
                        "metadata": "Banda Superior 80%"
                    }
                },
                {
                    "properties": {
                        "defaultColor": color_solid("#F59E0B")
                    },
                    "selector": {
                        "metadata": "Umbral P95"
                    }
                },
                {
                    "properties": {
                        "defaultColor": color_solid("#EF4444")
                    },
                    "selector": {
                        "metadata": "Evento Pico Estimado"
                    }
                }
            ],
            "lineStyles": [
                {
                    "properties": {
                        "strokeWidth": lit("2D"),
                        "lineStyle": lit("'solid'")
                    },
                    "selector": {
                        "metadata": "Demanda Real Ventana"
                    }
                },
                {
                    "properties": {
                        "strokeWidth": lit("2D"),
                        "lineStyle": lit("'solid'")
                    },
                    "selector": {
                        "metadata": "Demanda Pronosticada"
                    }
                },
                {
                    "properties": {
                        "strokeWidth": lit("1D"),
                        "lineStyle": lit("'dashed'")
                    },
                    "selector": {
                        "metadata": "Banda Inferior 80%"
                    }
                },
                {
                    "properties": {
                        "strokeWidth": lit("1D"),
                        "lineStyle": lit("'dashed'")
                    },
                    "selector": {
                        "metadata": "Banda Superior 80%"
                    }
                },
                {
                    "properties": {
                        "strokeWidth": lit("2D"),
                        "lineStyle": lit("'dashed'")
                    },
                    "selector": {
                        "metadata": "Umbral P95"
                    }
                },
                {
                    "properties": {
                        "strokeWidth": lit("0D"),
                        "lineStyle": lit("'solid'"),
                        "showMarker": lit("true"),
                        "markerShape": lit("'circle'"),
                        "markerSize": lit("6D"),
                        "markerColor": color_solid("#EF4444")
                    },
                    "selector": {
                        "metadata": "Evento Pico Estimado"
                    }
                }
            ],
            "legend": [{"properties": {
                "show": lit("true"),
                "position": lit("'Bottom'"),
                "fontSize": lit("10D"),
                "labelColor": color_solid("#0A2540")
            }}],
            "categoryAxis": [{"properties": {
                "show": lit("true"),
                "fontSize": lit("10D"),
                "labelColor": color_solid("#64748B"),
                "labelDisplayUnits": lit("0D")
            }}],
            "valueAxis": [{"properties": {
                "show": lit("true"),
                "fontSize": lit("10D"),
                "labelColor": color_solid("#64748B"),
                "labelDisplayUnits": lit("1000D"),
                "axisStyle": lit("'showTitleOnly'"),
                "showAxisTitle": lit("true"),
                "titleText": lit("'Demanda (unidades)'")
            }}],
            "plotArea": [{"properties": {
                "transparency": lit("0D")
            }}]
        },
        "visualContainerObjects": {
            "background": [{"properties": {
                "show": lit("true"),
                "color": color_solid("#FFFFFF"),
                "transparency": lit("0D")
            }}],
            "border": [{"properties": {
                "show": lit("true"),
                "color": color_solid("#E2E8F0"),
                "radius": lit("4D")
            }}],
            "padding": [{"properties": {
                "top": lit("8D"), "bottom": lit("8D"),
                "left": lit("12D"), "right": lit("12D")
            }}],
            "title": [{"properties": {
                "show": lit("true"),
                "text": lit("'📈 Demanda eléctrica: histórica y pronóstico'"),
                "fontSize": lit("12D"),
                "fontColor": color_solid("#0A2540"),
                "fontFamily": lit("'Segoe UI Semibold'")
            }}]
        }
    }
})

# ─── 15. DETAIL LEFT — Selected Point Detail ─────────────────────────────────
detail_left_id = vid("detail_left_table")
write_visual(detail_left_id, {
    "$schema": SCHEMA,
    "name": detail_left_id,
    "position": {"x": 276, "y": 761, "z": 2000, "height": 299, "width": 460, "tabOrder": 2010},
    "visual": {
        "visualType": "tableEx",
        "query": {
            "queryState": {
                "Values": {
                    "projections": [
                        {
                            "field": column_field("Dim_Calendario", "datetime"),
                            "queryRef": "Dim_Calendario.datetime",
                            "nativeQueryRef": "datetime"
                        },
                        proj("_Medidas", "Demanda Pronosticada"),
                        proj("_Medidas", "Banda Inferior 80%"),
                        proj("_Medidas", "Banda Superior 80%"),
                        proj("_Medidas", "Umbral P95"),
                        proj("_Medidas", "Probabilidad Pico Zona")
                    ]
                }
            }
        },
        "objects": {
            "columnHeaders": [{"properties": {
                "columnAdjustment": lit("'growToFit'"),
                "autoSizeColumnWidth": lit("true"),
                "fontColor": color_solid("#0A2540"),
                "fontSize": lit("10D"),
                "fontFamily": lit("'Segoe UI Semibold'"),
                "backColor": color_solid("#EFF6FF")
            }}],
            "values": [{"properties": {
                "fontColor": color_solid("#0A2540"),
                "fontSize": lit("10D"),
                "fontFamily": lit("'Segoe UI'")
            }}],
            "grid": [{"properties": {
                "gridVertical": lit("false"),
                "gridHorizontal": lit("true"),
                "gridHorizontalColor": color_solid("#E2E8F0"),
                "rowPadding": lit("3D")
            }}]
        },
        "visualContainerObjects": {
            "background": [{"properties": {
                "show": lit("true"),
                "color": color_solid("#FFFFFF"),
                "transparency": lit("0D")
            }}],
            "border": [{"properties": {
                "show": lit("true"),
                "color": color_solid("#E2E8F0"),
                "radius": lit("4D")
            }}],
            "padding": [{"properties": {
                "top": lit("8D"), "bottom": lit("8D"),
                "left": lit("12D"), "right": lit("12D")
            }}],
            "title": [{"properties": {
                "show": lit("true"),
                "text": lit("'📋 Detalle del punto seleccionado'"),
                "fontSize": lit("11D"),
                "fontColor": color_solid("#0A2540"),
                "fontFamily": lit("'Segoe UI Semibold'")
            }}]
        }
    }
})

# ─── 16. DETAIL MID — Upcoming High Demand Events ────────────────────────────
detail_mid_id = vid("detail_mid_events_table")
write_visual(detail_mid_id, {
    "$schema": SCHEMA,
    "name": detail_mid_id,
    "position": {"x": 752, "y": 761, "z": 2000, "height": 299, "width": 580, "tabOrder": 2011},
    "visual": {
        "visualType": "tableEx",
        "query": {
            "queryState": {
                "Values": {
                    "projections": [
                        {
                            "field": column_field("Fact_Eventos_Clasificacion", "datetime"),
                            "queryRef": "Fact_Eventos_Clasificacion.datetime",
                            "nativeQueryRef": "datetime"
                        },
                        {
                            "field": column_field("Dim_Zona", "zona_alias"),
                            "queryRef": "Dim_Zona.zona_alias",
                            "nativeQueryRef": "zona_alias"
                        },
                        proj("_Medidas", "Demanda Pronosticada"),
                        {
                            "field": {
                                "Aggregation": {
                                    "Expression": column_field("Fact_Eventos_Clasificacion", "probabilidad"),
                                    "Function": 1
                                }
                            },
                            "queryRef": "Avg(Fact_Eventos_Clasificacion.probabilidad)",
                            "nativeQueryRef": "probabilidad"
                        },
                        {
                            "field": column_field("Fact_Eventos_Clasificacion", "estado_predicho"),
                            "queryRef": "Fact_Eventos_Clasificacion.estado_predicho",
                            "nativeQueryRef": "estado_predicho"
                        }
                    ]
                }
            },
            "sortDefinition": {
                "sort": [{
                    "field": {
                        "Aggregation": {
                            "Expression": column_field("Fact_Eventos_Clasificacion", "probabilidad"),
                            "Function": 1
                        }
                    },
                    "direction": "Descending"
                }],
                "isDefaultSort": False
            }
        },
        "objects": {
            "columnHeaders": [{"properties": {
                "columnAdjustment": lit("'growToFit'"),
                "autoSizeColumnWidth": lit("true"),
                "fontColor": color_solid("#0A2540"),
                "fontSize": lit("10D"),
                "fontFamily": lit("'Segoe UI Semibold'"),
                "backColor": color_solid("#FFF7ED")
            }}],
            "values": [{"properties": {
                "fontColor": color_solid("#0A2540"),
                "fontSize": lit("10D"),
                "fontFamily": lit("'Segoe UI'")
            }}],
            "grid": [{"properties": {
                "gridVertical": lit("false"),
                "gridHorizontal": lit("true"),
                "gridHorizontalColor": color_solid("#E2E8F0"),
                "rowPadding": lit("3D")
            }}]
        },
        "visualContainerObjects": {
            "background": [{"properties": {
                "show": lit("true"),
                "color": color_solid("#FFFFFF"),
                "transparency": lit("0D")
            }}],
            "border": [{"properties": {
                "show": lit("true"),
                "color": color_solid("#E2E8F0"),
                "radius": lit("4D")
            }}],
            "padding": [{"properties": {
                "top": lit("8D"), "bottom": lit("8D"),
                "left": lit("12D"), "right": lit("12D")
            }}],
            "title": [{"properties": {
                "show": lit("true"),
                "text": lit("'🔔 Próximos eventos de demanda elevada'"),
                "fontSize": lit("11D"),
                "fontColor": color_solid("#D97706"),
                "fontFamily": lit("'Segoe UI Semibold'")
            }}]
        }
    }
})

# ─── 17. DETAIL RIGHT — Zone Comparison Table ─────────────────────────────────
detail_right_id = vid("detail_right_zone_comp")
write_visual(detail_right_id, {
    "$schema": SCHEMA,
    "name": detail_right_id,
    "position": {"x": 1348, "y": 761, "z": 2000, "height": 299, "width": 572, "tabOrder": 2012},
    "visual": {
        "visualType": "tableEx",
        "query": {
            "queryState": {
                "Values": {
                    "projections": [
                        {
                            "field": column_field("Dim_Zona", "zona_alias"),
                            "queryRef": "Dim_Zona.zona_alias",
                            "nativeQueryRef": "zona_alias"
                        },
                        proj("_Medidas", "Demanda Media Prevista"),
                        proj("_Medidas", "Pico Estimado"),
                        proj("_Medidas", "Probabilidad Promedio de Pico por Zona")
                    ]
                }
            },
            "sortDefinition": {
                "sort": [{
                    "field": column_field("Dim_Zona", "zona_alias"),
                    "direction": "Ascending"
                }],
                "isDefaultSort": True
            }
        },
        "objects": {
            "columnHeaders": [{"properties": {
                "columnAdjustment": lit("'growToFit'"),
                "autoSizeColumnWidth": lit("true"),
                "fontColor": color_solid("#0A2540"),
                "fontSize": lit("10D"),
                "fontFamily": lit("'Segoe UI Semibold'"),
                "backColor": color_solid("#EFF6FF")
            }}],
            "values": [{"properties": {
                "fontColor": color_solid("#0A2540"),
                "fontSize": lit("10D"),
                "fontFamily": lit("'Segoe UI'")
            }}],
            "grid": [{"properties": {
                "gridVertical": lit("false"),
                "gridHorizontal": lit("true"),
                "gridHorizontalColor": color_solid("#E2E8F0"),
                "rowPadding": lit("3D")
            }}]
        },
        "visualContainerObjects": {
            "background": [{"properties": {
                "show": lit("true"),
                "color": color_solid("#FFFFFF"),
                "transparency": lit("0D")
            }}],
            "border": [{"properties": {
                "show": lit("true"),
                "color": color_solid("#E2E8F0"),
                "radius": lit("4D")
            }}],
            "padding": [{"properties": {
                "top": lit("8D"), "bottom": lit("8D"),
                "left": lit("12D"), "right": lit("12D")
            }}],
            "title": [{"properties": {
                "show": lit("true"),
                "text": lit("'📊 Comparativo por zona (próximas 24 h)'"),
                "fontSize": lit("11D"),
                "fontColor": color_solid("#0A2540"),
                "fontFamily": lit("'Segoe UI Semibold'")
            }}]
        }
    }
})

print("18 visuals generados exitosamente en:")
print(f"  {VISUALS_DIR}")

