import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

###############
##### GYM #####
###############

# Facility IDs for UCLA Recreation API
FACILITY_IDS = {"bfit": 803, "john-wooden-center": 802}

# URLs for scraping
FACILITY_COUNT_URL = "https://goboardapi.azurewebsites.net/api/FacilityCount/GetCountsByAccount?AccountAPIKey=73829a91-48cb-4b7b-bd0b-8cf4134c04cd"
BFIT_URL = "https://recreation.ucla.edu/facilities/bfit"
JWC_URL = "https://recreation.ucla.edu/facilities/jwc"



###################
##### LIBRARY #####
###################

# Library reservation URLs
POWELL_URL = "https://calendar.library.ucla.edu/reserve/spaces/powell"
YRL_URL = "https://calendar.library.ucla.edu/reserve/spaces/yrl"
MUSIC_LIBRARY_URL = "https://calendar.library.ucla.edu/reserve/spaces/musickits"
BIOMEDICAL_LIBRARY_URL = "https://calendar.library.ucla.edu/spaces?lid=6578"
SEL_URL = "https://calendar.library.ucla.edu/reserve/spaces/SEL"
MEDIA_LAB_URL = "https://calendar.library.ucla.edu/spaces?lid=19391"

ALL_LIBRARY_URLS = [POWELL_URL, YRL_URL, MUSIC_LIBRARY_URL,
                    BIOMEDICAL_LIBRARY_URL, SEL_URL, MEDIA_LAB_URL]
LIBRARY_GRID_ENDPOINT = "https://calendar.library.ucla.edu/spaces/availability/grid"

LIBRARY_LID_MAP = {
    POWELL_URL: 4361,
    YRL_URL: 5567,
    MUSIC_LIBRARY_URL: 4752,
    BIOMEDICAL_LIBRARY_URL: 6578,
    SEL_URL: 8312,
    MEDIA_LAB_URL: 19391
}

LIBRARY_GID_MAP = {
    POWELL_URL: 7748,
    YRL_URL: 7750,
    MUSIC_LIBRARY_URL: 7750,
    BIOMEDICAL_LIBRARY_URL: 11674,
    SEL_URL: 14408,
    MEDIA_LAB_URL: 40875
}

LIBRARY_URL_CONFIG = {
    library_url: {
        "params": {"lid": None},
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            # "Content-Length": "0",
            "Host": "calendar.library.ucla.edu",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Origin": "https://calendar.library.ucla.edu",
            "Referer": library_url
        },
        "payload": {
            "lid": LIBRARY_LID_MAP[library_url],
            "gid": LIBRARY_GID_MAP[library_url],
            "start": None,  # TODO: Update to be flexible input
            "end": None,  # TODO: Update to be flexible input
            "pageSize": 1
        }
    }
    for library_url in ALL_LIBRARY_URLS
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


###################
###### DINING #####
###################


OCCUSPACE_PREFIX = "https://testing.occuspace.io/waitz/location"
MENUS_PREFIX = "https://menu.dining.ucla.edu/Menus"

RESTAURANTS = {
    "bplate": "BruinPlate",
    "deneve": "DeNeve",
    "epicuria": "Epicuria"
}

# From https://testing.occuspace.io/waitz/customer/21/locations
OCCUSPACE_IDS: dict[str, int] = {
    "epicuria": 88,
    "bplate": 77,
    "deneve": 78,
}