import re

TAG_RE = re.compile(r'<[^>]+>')
CATEGORIES = {
    "guys": {
        "teesandbasics": "Tees + Graphics",
        "henleysandpolos": "Henleys + Polos",
        "buttondowns": "Button Downs",
        "outerwear": "Hoodies + Outerwear",
        "bottoms": "Bottoms",
        "lastcall": "Last Call",
        "boxers": "Boxers",
        "sunglasseshats": "Hats + Sunglasses",
        "sweater": "Sweaters"
    },
    "gals": {
        "teesandbasics": "Tees + Basics",
        "tops": "Shirts + Tops",
        "outerwear": "Outerwear",
        "sweater": "Sweaters",
        "dresses": "Dresses + Jumpsuits",
        "bottoms": "Bottoms + Skirts",
        "lastcall": "Last Call"
    },
    "mini": {
        "girls": "Girls",
        "boys": "Boys",
        "lastcall": "Last Call"
    },
    "giftcards": {}
}
