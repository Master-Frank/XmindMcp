"""Default XMind presentation; kept outside the document model."""
from ..models import generate_id


def create_json_structure(title, children):
    """Create JSON structure"""
    return {
        "id": generate_id(),
        "class": "sheet",
        "rootTopic": {
            "id": generate_id(),
            "class": "topic",
            "title": title,
            "structureClass": "org.xmind.ui.logic.right",
            "children": {
                "attached": children
            }
        },
        "title": "画布 1",
        "extensions": [{
            "provider": "org.xmind.ui.skeleton.structure.style",
            "content": {
                "centralTopic": "org.xmind.ui.logic.right"
            }
        }],
        "theme": {
            "map": {
                "id": generate_id(),
                "properties": {
                    "svg:fill": "#ffffff",
                    "multi-line-colors": "#F9423A #F6A04D #F3D321 #00BC7B #486AFF #4D49BE",
                    "color-list": "#000229 #1F2766 #52CC83 #4D86DB #99142F #245570",
                    "line-tapered": "none"
                }
            },
            "centralTopic": {
                "id": generate_id(),
                "properties": {
                    "fo:font-family": "Droid Serif",
                    "fo:font-size": "30pt",
                    "fo:font-weight": "400",
                    "fo:font-style": "normal",
                    "fo:color": "inherited",
                    "fo:text-transform": "manual",
                    "fo:text-decoration": "none",
                    "fo:text-align": "center",
                    "svg:fill": "#000229",
                    "fill-pattern": "solid",
                    "line-width": "3pt",
                    "line-color": "#000229",
                    "line-pattern": "solid",
                    "border-line-color": "inherited",
                    "border-line-width": "3pt",
                    "border-line-pattern": "inherited",
                    "shape-class": "org.xmind.topicShape.roundedRect",
                    "line-class": "org.xmind.branchConnection.roundedElbow",
                    "arrow-end-class": "org.xmind.arrowShape.none",
                    "alignment-by-level": "inactived"
                }
            },
            "mainTopic": {
                "id": generate_id(),
                "properties": {
                    "fo:font-family": "Droid Serif",
                    "fo:font-size": "18pt",
                    "fo:font-weight": "400",
                    "fo:font-style": "normal",
                    "fo:color": "inherited",
                    "fo:text-transform": "manual",
                    "fo:text-decoration": "none",
                    "fo:text-align": "left",
                    "svg:fill": "inherited",
                    "fill-pattern": "none",
                    "line-width": "inherited",
                    "line-color": "inherited",
                    "line-pattern": "inherited",
                    "border-line-color": "inherited",
                    "border-line-width": "0pt",
                    "border-line-pattern": "inherited",
                    "shape-class": "org.xmind.topicShape.roundedRect",
                    "line-class": "org.xmind.branchConnection.roundedElbow",
                    "arrow-end-class": "inherited"
                }
            },
            "subTopic": {
                "id": generate_id(),
                "properties": {
                    "fo:font-family": "Droid Serif",
                    "fo:font-size": "14pt",
                    "fo:font-weight": "400",
                    "fo:font-style": "normal",
                    "fo:color": "inherited",
                    "fo:text-transform": "manual",
                    "fo:text-decoration": "none",
                    "fo:text-align": "left",
                    "svg:fill": "inherited",
                    "fill-pattern": "none",
                    "line-width": "2pt",
                    "line-color": "inherited",
                    "line-pattern": "inherited",
                    "border-line-color": "inherited",
                    "border-line-width": "0pt",
                    "border-line-pattern": "inherited",
                    "shape-class": "org.xmind.topicShape.roundedRect",
                    "line-class": "org.xmind.branchConnection.roundedElbow",
                    "arrow-end-class": "inherited"
                }
            },
            "skeletonThemeId": "c1fbada1b45ba2e3bfc3b8b57b",
            "colorThemeId": "Rainbow-#000229-MULTI_LINE_COLORS"
        }
    }
