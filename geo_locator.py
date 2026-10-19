# ============================================================
# NSFDC SETU
# CHANNEL PARTNER GEO LOCATOR
# ============================================================

import json
from pathlib import Path

from geopy.distance import geodesic


# ============================================================
# PARTNER FILE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DEFAULT_PARTNER_FILE = (
    BASE_DIR / "data" / "odisha_partners.json"
)


# ============================================================
# LOAD PARTNERS
# ============================================================

def load_partners(file_path=DEFAULT_PARTNER_FILE):

    file_path = Path(file_path)

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)


    # --------------------------------------------------------
    # Support:
    #
    # [
    #   {...},
    #   {...}
    # ]
    #
    # AND
    #
    # {
    #   "partners": [...]
    # }
    # --------------------------------------------------------

    if isinstance(data, dict):

        if "partners" in data:

            data = data["partners"]

        elif "channel_partners" in data:

            data = data["channel_partners"]

        else:

            raise ValueError(
                "Partner JSON does not contain "
                "'partners' or 'channel_partners'."
            )


    if not isinstance(data, list):

        raise ValueError(
            "Partner data must be a list."
        )


    return data


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize(value):

    if value is None:

        return ""

    return str(
        value
    ).strip().lower()


# ============================================================
# SCHEME ALIASES
# ============================================================

SCHEME_ALIASES = {

    "MFS": {

        "mfs",
        "micro finance scheme",
        "microfinance scheme",
        "micro-finance scheme"

    },

    "TL": {

        "tl",
        "term loan",
        "term loan scheme"

    },

    "EDU": {

        "edu",
        "education",
        "education loan",
        "education loan scheme"

    }

}


# ============================================================
# CONVERT ANY SCHEME VALUE TO CANONICAL ID
# ============================================================

def canonical_scheme_id(value):

    value = normalize(
        value
    )


    for scheme_id, aliases in SCHEME_ALIASES.items():

        if value in aliases:

            return scheme_id


    return value.upper()


# ============================================================
# GET PARTNER SCHEMES
# ============================================================

def get_partner_schemes(partner):

    """
    Supports multiple possible JSON field names.

    Preferred:
        handles_schemes

    Also accepts:
        schemes
        supported_schemes
        scheme_ids
        handlesSchemes
    """

    possible_fields = [

        "handles_schemes",

        "supported_schemes",

        "scheme_ids",

        "schemes",

        "handlesSchemes"

    ]


    for field in possible_fields:

        if field not in partner:

            continue


        value = partner.get(
            field
        )


        if value is None:

            continue


        if isinstance(
            value,
            str
        ):

            value = [
                value
            ]


        if isinstance(
            value,
            list
        ):

            return value


    return []


# ============================================================
# CHECK SCHEME
# ============================================================

def supports_scheme(
    partner,
    scheme_id
):

    requested_scheme = canonical_scheme_id(
        scheme_id
    )


    partner_schemes = get_partner_schemes(
        partner
    )


    for partner_scheme in partner_schemes:

        partner_scheme_id = canonical_scheme_id(
            partner_scheme
        )


        if partner_scheme_id == requested_scheme:

            return True


    return False


# ============================================================
# FIND NEAREST PARTNERS
# ============================================================

def get_nearest_partner_results(

    user_lat,
    user_lon,
    scheme_id,
    partners,
    top_n=3

):

    # ========================================================
    # VALIDATE PARTNERS
    # ========================================================

    if not partners:

        return {

            "success": False,

            "count": 0,

            "partners": [],

            "message":
                "Partner database is empty."

        }


    # ========================================================
    # USER LOCATION
    # ========================================================

    try:

        user_lat = float(
            user_lat
        )

        user_lon = float(
            user_lon
        )

    except (
        TypeError,
        ValueError
    ):

        return {

            "success": False,

            "count": 0,

            "partners": [],

            "message":
                "Invalid district coordinates."

        }


    user_location = (

        user_lat,
        user_lon

    )


    # ========================================================
    # SEARCH PARTNERS
    # ========================================================

    results = []


    for partner in partners:

        if not isinstance(
            partner,
            dict
        ):

            continue


        # ----------------------------------------------------
        # SCHEME CHECK
        # ----------------------------------------------------

        if not supports_scheme(
            partner,
            scheme_id
        ):

            continue


        # ----------------------------------------------------
        # LOCATION
        # ----------------------------------------------------

        try:

            partner_lat = float(

                partner.get(
                    "lat"
                )

            )

            partner_lon = float(

                partner.get(
                    "lon"
                )

            )

        except (
            TypeError,
            ValueError
        ):

            continue


        # ----------------------------------------------------
        # DISTANCE
        # ----------------------------------------------------

        distance = geodesic(

            user_location,

            (
                partner_lat,
                partner_lon
            )

        ).km


        # ----------------------------------------------------
        # COPY
        # ----------------------------------------------------

        result = dict(
            partner
        )


        result["lat"] = (
            partner_lat
        )

        result["lon"] = (
            partner_lon
        )

        result["distance_km"] = round(
            distance,
            1
        )


        results.append(
            result
        )


    # ========================================================
    # SORT
    # ========================================================

    results.sort(

        key=lambda item:
            item[
                "distance_km"
            ]

    )


    # ========================================================
    # TOP N
    # ========================================================

    results = results[
        :int(top_n)
    ]


    # ========================================================
    # RETURN
    # ========================================================

    return {

        "success": True,

        "count":
            len(results),

        "partners":
            results,

        "user_location": {

            "lat":
                user_lat,

            "lon":
                user_lon

        },

        "scheme_id":
            canonical_scheme_id(
                scheme_id
            )

    }


# ============================================================
# SIMPLE FUNCTION
# ============================================================

def get_nearest_partners(

    user_lat,
    user_lon,
    scheme_id,
    partners,
    top_n=3

):

    result = get_nearest_partner_results(

        user_lat,

        user_lon,

        scheme_id,

        partners,

        top_n

    )


    return result[
        "partners"
    ]