"""
Useful constants
"""

PITCH_LENGTH_M = 105
PITCH_WIDTH_M = 68

METRICA_EVENTS_METADATA = [
    {"category": "TYPE", "name": "PASS", "id": "1"},
    {"category": "TYPE", "name": "SHOT", "id": "2"},
    {"category": "TYPE", "name": "RECOVERY", "id": "3"},
    {"category": "TYPE", "name": "FAULT RECEIVED", "id": "4"},
    {"category": "TYPE", "name": "SET PIECE", "id": "5"},
    {"category": "TYPE", "name": "BALL OUT", "id": "6"},
    {"category": "TYPE", "name": "BALL LOST", "id": "7"},
    {"category": "TYPE", "name": "CARD", "id": "8"},
    {"category": "TYPE", "name": "CHALLENGE", "id": "9"},
    {"category": "TYPE", "name": "CARRY", "id": "10"},
    {"category": "SUBTYPE", "name": "HEAD", "id": "11"},
    {"category": "SUBTYPE", "name": "CLEARANCE", "id": "12"},
    {"category": "SUBTYPE", "name": "CROSS", "id": "13"},
    {"category": "SUBTYPE", "name": "THROUGH BALL", "id": "14"},
    {"category": "SUBTYPE", "name": "DEEP BALL", "id": "15"},
    {"category": "SUBTYPE", "name": "OFFSIDE", "id": "16"},
    {"category": "SUBTYPE", "name": "VOLUNTARY", "id": "17"},
    {"category": "SUBTYPE", "name": "FORCED", "id": "18"},
    {"category": "SUBTYPE", "name": "END HALF", "id": "19"},
    {"category": "SUBTYPE", "name": "GOAL KICK", "id": "20"},
    {"category": "SUBTYPE", "name": "HAND BALL", "id": "21"},
    {"category": "SUBTYPE", "name": "REFEREE HIT", "id": "22"},
    {"category": "SUBTYPE", "name": "INTERCEPTION", "id": "23"},
    {"category": "SUBTYPE", "name": "THEFT", "id": "24"},
    {"category": "SUBTYPE", "name": "BLOCKED", "id": "25"},
    {"category": "SUBTYPE", "name": "SAVED", "id": "26"},
    {"category": "SUBTYPE", "name": "WOODWORK", "id": "27"},
    {"category": "SUBTYPE", "name": "ON TARGET", "id": "28"},
    {"category": "SUBTYPE", "name": "OFF TARGET", "id": "29"},
    {"category": "SUBTYPE", "name": "GOAL", "id": "30"},
    {"category": "SUBTYPE", "name": "OUT", "id": "31"},
    {"category": "SUBTYPE", "name": "FREE KICK", "id": "32"},
    {"category": "SUBTYPE", "name": "CORNER KICK", "id": "33"},
    {"category": "SUBTYPE", "name": "THROW IN", "id": "34"},
    {"category": "SUBTYPE", "name": "KICK OFF", "id": "35"},
    {"category": "SUBTYPE", "name": "PENALTY", "id": "36"},
    {"category": "SUBTYPE", "name": "DIRECT", "id": "37"},
    {"category": "SUBTYPE", "name": "INDIRECT", "id": "38"},
    {"category": "SUBTYPE", "name": "RETAKEN", "id": "39"},
    {"category": "SUBTYPE", "name": "YELLOW", "id": "40"},
    {"category": "SUBTYPE", "name": "RED", "id": "41"},
    {"category": "SUBTYPE", "name": "GROUND", "id": "42"},
    {"category": "SUBTYPE", "name": "AERIAL", "id": "43"},
    {"category": "SUBTYPE", "name": "TACKLE", "id": "44"},
    {"category": "SUBTYPE", "name": "DRIBBLE", "id": "45"},
    {"category": "SUBTYPE", "name": "FAULT", "id": "46"},
    {"category": "SUBTYPE", "name": "ADVANTAGE", "id": "47"},
    {"category": "SUBTYPE", "name": "WON", "id": "48"},
    {"category": "SUBTYPE", "name": "LOST", "id": "49"},
]

METRICA_EVENT_TYPES = [
    event for event in METRICA_EVENTS_METADATA if event["category"] == "TYPE"
]
METRICA_SUBEVENT_TYPES = [
    event for event in METRICA_EVENTS_METADATA if event["category"] == "SUBTYPE"
]
