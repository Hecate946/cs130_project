import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

# Facility IDs for UCLA Recreation API
FACILITY_IDS = {"bfit": 803, "john-wooden-center": 802}

# URLs for scraping
FACILITY_COUNT_URL = "https://goboardapi.azurewebsites.net/api/FacilityCount/GetCountsByAccount?AccountAPIKey=73829a91-48cb-4b7b-bd0b-8cf4134c04cd"
BFIT_URL = "https://recreation.ucla.edu/facilities/bfit"
JWC_URL = "https://recreation.ucla.edu/facilities/jwc"


POWELL = "Powell Library"
YRL = "Young Research Library"
MUSIC_LIBRARY = "Walter H. Rubsamen Music Library"
BIOMEDICAL = "Louise M. Darling Biomedical Library"
SEL = "Science and Engineering Library"
MEDIA_LAB = "Media Lab"

# Library reservation URLs
POWELL_URL = "https://calendar.library.ucla.edu/reserve/spaces/powell"
YRL_URL = "https://calendar.library.ucla.edu/reserve/spaces/yrl"
MUSIC_LIBRARY_URL = "https://calendar.library.ucla.edu/reserve/spaces/musickits"
BIOMEDICAL_URL = "https://calendar.library.ucla.edu/spaces?lid=6578"
SEL_URL = "https://calendar.library.ucla.edu/reserve/spaces/SEL"
MEDIA_LAB_URL = "https://calendar.library.ucla.edu/spaces?lid=19391"



LIBRARY_NAME_TO_URL_MAP = {
    POWELL: POWELL_URL,
    YRL: YRL_URL,
    MUSIC_LIBRARY: MUSIC_LIBRARY_URL,
    BIOMEDICAL: BIOMEDICAL_URL,
    SEL: SEL_URL,
    MEDIA_LAB: MEDIA_LAB_URL
}

LIBRARY_URL_TO_NAME_MAP = {
    POWELL_URL: POWELL,
    YRL_URL: YRL,
    MUSIC_LIBRARY_URL: MUSIC_LIBRARY,
    BIOMEDICAL_URL: BIOMEDICAL,
    SEL_URL: SEL,
    MEDIA_LAB_URL: MEDIA_LAB
}

ALL_LIBRARY_URLS = [POWELL_URL, YRL_URL, MUSIC_LIBRARY_URL,
                    BIOMEDICAL_URL, SEL_URL, MEDIA_LAB_URL]

ALL_LIBRARY_NAMES = [POWELL, YRL, MUSIC_LIBRARY,
                     BIOMEDICAL, SEL, MEDIA_LAB]

LIBRARY_GRID_ENDPOINT = "https://calendar.library.ucla.edu/spaces/availability/grid"

LIBRARY_LID_MAP = {
    POWELL: 4361,
    YRL: 5567,
    MUSIC_LIBRARY: 4752,
    BIOMEDICAL: 6578,
    SEL: 8312,
    MEDIA_LAB: 19391
}

LIBRARY_GID_MAP = {
    POWELL: 7748,
    YRL: 7750,
    MUSIC_LIBRARY: 7750,
    BIOMEDICAL: 11674,
    SEL: 14408,
    MEDIA_LAB: 40875
}

LIBRARY_URL_CONFIG = {
    library_name: {
        "library_url": LIBRARY_NAME_TO_URL_MAP[library_name],
        "params": {"lid": None},
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            # "Content-Length": "0",
            "Host": "calendar.library.ucla.edu",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Origin": "https://calendar.library.ucla.edu",
            "Referer": LIBRARY_NAME_TO_URL_MAP[library_name]
        },
        "payload": {
            "lid": LIBRARY_LID_MAP[library_name],
            "gid": LIBRARY_GID_MAP[library_name],
            "start": None,  # TODO: Update to be flexible input
            "end": None,  # TODO: Update to be flexible input
            "pageSize": 1
        },
    }
    for library_name in ALL_LIBRARY_NAMES
}

LIBRARY_EID_TO_NAME_MAP = {
    29694: "Powell Group Study Room A (Capacity 8)",
    29695: "Powell Group Study Room B (Capacity 8)",
    29696: "Powell Group Study Room C (Capacity 8)",
    29697: "Powell Group Study Room D (Capacity 8)",
    29698: "Powell Group Study Room E (Capacity 8)",
    29699: "Powell Group Study Room F (Capacity 8)",
    29719: "YRL Collaboration Pod R01 (Capacity 7)",
    29720: "YRL Collaboration Pod R02 (Capacity 7)",
    29721: "YRL Collaboration Pod R03 (Capacity 8)",
    29722: "YRL Collaboration Pod R04 (Capacity 8)",
    29723: "YRL Collaboration Pod R05 (Capacity 8)",
    29724: "YRL Collaboration Pod R06 (Capacity 8)",
    29725: "YRL Collaboration Pod R07 (Capacity 8)",
    29726: "YRL Collaboration Pod R08 (Capacity 8)",
    29727: "YRL Collaboration Pod R09 (Capacity 8)",
    29729: "YRL Collaboration Pod R11 (Capacity 8)",
    29730: "YRL Collaboration Pod R12 (Capacity 8)",
    29731: "YRL Collaboration Pod R13 (Capacity 8)",
    29732: "YRL Collaboration Pod R14 (Capacity 8)",
    29733: "YRL Collaboration Pod R15 (Capacity 8)",
    29734: "YRL Collaboration Pod R16 (Capacity 8)",
    29735: "YRL Collaboration Pod R17 (Capacity 8)",
    29736: "YRL Collaboration Pod R18 (Capacity 8)",
    29737: "YRL Collaboration Pod R19 (Capacity 8)",
    29738: "YRL Collaboration Pod R20 (Capacity 8)",
    55358: "Music Library Seminar Room (Capacity 20)",
    44647: "12-077E Group Study Room (Capacity 8)",
    55389: "Boelter 8251A - SEL/Research Commons (Capacity 8)",
    55390: "Geology 4697A - SEL/Geology Collection (Capacity 8)",
    55391: "Geology 4697B - SEL/Geology Collection (Capacity 4)",
    165438: "Room 2 (Capacity 4)",
    165439: "Room 3 (Capacity 4)",
    165440: "Room 5 (Capacity 4)",
    165441: "Room 6 (Capacity 4)"
}

OCCUSPACE_PREFIX = "https://testing.occuspace.io/waitz/location/"
MENUS_PREFIX = "https://menu.dining.ucla.edu/Menus/"
