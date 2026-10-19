import re
import json
from pathlib import Path

import streamlit as st

from deep_translator import GoogleTranslator
from geopy.distance import geodesic


# ============================================================
# SETUP
# ============================================================

BASE_DIR = Path(__file__).resolve().parent


# ============================================================
# DISTRICT LOCATIONS
# ============================================================

DISTRICT_LOCATIONS = {

    "bhubaneswar": (20.2961, 85.8245),

    "khordha": (20.22565, 85.56059),

    "cuttack": (20.4640, 85.8792),

    "jajpur": (20.85227, 86.33857),

    "dhenkanal": (20.6574, 85.5963),

    "jagatsinghpur": (20.25939, 86.16609),

    "rourkela": (22.2604, 84.8536),

    "sambalpur": (21.4669, 83.9750),

    "sundargarh": (22.11667, 84.03333),

    "angul": (20.84903, 85.06079),

    "boudh": (20.83773, 84.32618),

    "balangir": (20.70419, 83.49029),

    "bargarh": (21.33348, 83.61905),

    "balasore": (21.49266, 86.93348),

    "bhadrak": (21.05447, 86.51561),

    "deogarh": (21.53708, 84.73012),

    "gajapati": (18.7816, 84.0880),

    "ganjam": (19.3551, 84.9836),

    "jharsuguda": (21.87705, 84.00905),

    "keonjhar": (21.58923, 85.66878),

    "kalahandi": (19.90717, 83.16698),

    "kandhamal": (20.4740, 84.2309),

    "koraput": (18.8135, 82.7123),

    "kendrapara": (20.5004, 86.4317),

    "malkangiri": (18.3480, 81.8920),

    "mayurbhanj": (21.93459, 86.72852),

    "nabarangpur": (19.23114, 82.54826),

    "nuapada": (20.7691, 82.51863),

    "nayagarh": (20.11607, 85.11196),

    "puri": (19.80761, 85.82525),

    "rayagada": (19.1716, 83.4163),

    "subarnapur": (20.8330, 83.9160)

}


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def get_cached_data():

    schemes_path = (
        BASE_DIR /
        "data" /
        "schemes.json"
    )

    partners_path = (
        BASE_DIR /
        "data" /
        "odisha_partners.json"
    )

    try:

        with open(
            schemes_path,
            "r",
            encoding="utf-8"
        ) as f:

            schemes = json.load(f)


        with open(
            partners_path,
            "r",
            encoding="utf-8"
        ) as f:

            partners = json.load(f)


        return schemes, partners

    except Exception:

        return [], []


schemes_data, partners_data = get_cached_data()


# ============================================================
# TRANSLATION
# ============================================================

def translate_text(
    text: str,
    lang_code: str
) -> str:

    if (
        lang_code == "en"
        or not text.strip()
    ):

        return text


    try:

        return GoogleTranslator(
            source="auto",
            target=lang_code
        ).translate(text)

    except Exception:

        return text


# ============================================================
# EXTRACT COST
# ============================================================

def extract_cost(
    text: str
):

    clean = (
        text
        .lower()
        .replace(",", "")
    )


    # Examples:
    # 1 lakh
    # 1.5 lakh
    # 5 lakhs
    # 2L

    lakh_match = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:lakh|lakhs|l)\b",
        clean
    )


    if lakh_match:

        return (
            float(lakh_match.group(1))
            * 100000
        )


    # Normal numbers
    # 100000
    # 500000
    # 5000000

    num_match = re.search(
        r"\b\d{4,8}\b",
        clean
    )


    if num_match:

        return float(
            num_match.group(0)
        )


    return None


# ============================================================
# EXTRACT PURPOSE
# ============================================================

def extract_purpose(
    text: str
) -> str:

    clean = text.lower()


    education_words = [
        "education",
        "edu",
        "college",
        "study",
        "student",
        "course",
        "school",
        "degree",
        "university",
        "abroad"
    ]


    if any(
        word in clean
        for word in education_words
    ):

        return "education"


    return "project"


# ============================================================
# EXTRACT DISTRICT
# ============================================================

def extract_district(text: str):

    clean = text.lower()


    for district, coords in DISTRICT_LOCATIONS.items():

        if district in clean:

            return (
                district.title(),
                coords
            )


    return None


# ============================================================
# EMI CALCULATOR
# ============================================================

def calculate_emi_internal(
    principal: float,
    annual_rate: float,
    tenure_years: float,
    moratorium_months: int = 0
):

    monthly_rate = (
        annual_rate / 100
    ) / 12


    repayment_months = int(
        tenure_years * 12
    )


    accrued_interest = (
        principal
        * monthly_rate
        * moratorium_months
    )


    adjusted_principal = (
        principal
        + accrued_interest
    )


    if monthly_rate == 0:

        emi = (
            adjusted_principal
            / repayment_months
        )

    else:

        emi = (
            adjusted_principal
            * monthly_rate
            * (1 + monthly_rate)
            ** repayment_months
        ) / (
            (1 + monthly_rate)
            ** repayment_months
            - 1
        )


    return (
        round(emi, 2),
        round(adjusted_principal, 2)
    )


# ============================================================
# SCHEME + EMI ENGINE
# ============================================================

def execute_scheme_and_emi(
    purpose: str,
    cost: float
) -> str:

    if not schemes_data:

        return (
            "Schemes database is currently unavailable. "
            "Please ensure data/schemes.json exists."
        )


    target_scheme = None


    # --------------------------------------------------------
    # Education
    # --------------------------------------------------------

    if purpose == "education":

        target_scheme = next(
            (
                scheme
                for scheme in schemes_data
                if scheme.get("scheme_id") == "EDU"
            ),
            None
        )


    # --------------------------------------------------------
    # Micro Finance Scheme
    # --------------------------------------------------------

    elif cost <= 140000:

        target_scheme = next(
            (
                scheme
                for scheme in schemes_data
                if scheme.get("scheme_id") == "MFS"
            ),
            None
        )


    # --------------------------------------------------------
    # Term Loan
    # --------------------------------------------------------

    elif cost <= 5000000:

        target_scheme = next(
            (
                scheme
                for scheme in schemes_data
                if scheme.get("scheme_id") == "TL"
            ),
            None
        )


    else:

        return (
            f"A project cost of ₹{cost:,.0f} "
            "exceeds the maximum ₹50,00,000 "
            "project cost supported by the current "
            "loaded project schemes."
        )


    if not target_scheme:

        return (
            "No matching scheme was found."
        )


    # --------------------------------------------------------
    # Maximum loan
    # --------------------------------------------------------

    loan_percentage = float(
        target_scheme[
            "max_loan_pct_of_cost"
        ]
    )


    max_loan = (
        cost
        * loan_percentage
        / 100
    )


    if target_scheme.get(
        "max_loan_amount"
    ):

        max_loan = min(
            max_loan,
            float(
                target_scheme[
                    "max_loan_amount"
                ]
            )
        )


    # --------------------------------------------------------
    # Interest
    # --------------------------------------------------------

    rate = float(
        target_scheme[
            "interest_rate_beneficiary"
        ]
    )


    # --------------------------------------------------------
    # Tenure
    # --------------------------------------------------------

    tenure = float(
        target_scheme[
            "max_tenure_years"
        ]
    )


    # --------------------------------------------------------
    # Moratorium
    # --------------------------------------------------------

    moratorium = target_scheme.get(
        "moratorium_months",
        0
    )


    if isinstance(
        moratorium,
        list
    ):

        moratorium = moratorium[0]


    elif not isinstance(
        moratorium,
        int
    ):

        moratorium = 0


    # --------------------------------------------------------
    # EMI
    # --------------------------------------------------------

    emi, adjusted_principal = (
        calculate_emi_internal(
            max_loan,
            rate,
            tenure,
            moratorium
        )
    )


    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    response = (
        f"### 🏦 Recommended Scheme\n\n"

        f"**{target_scheme['name']} "
        f"({target_scheme['scheme_id']})**\n\n"

        f"**Estimated Cost:** "
        f"₹{cost:,.0f}\n\n"

        f"**Maximum Loan Eligible:** "
        f"₹{max_loan:,.0f}\n\n"

        f"**Interest Rate:** "
        f"{rate}% per annum\n\n"

        f"**Repayment Tenure:** "
        f"{int(tenure)} years\n\n"

        f"**Moratorium:** "
        f"{moratorium} months\n\n"

        f"### 💰 Estimated Monthly EMI\n\n"

        f"**₹{emi:,.2f}**\n\n"

        f"_{target_scheme['description']}_"
    )


    return response


# ============================================================
# PARTNER LOCATOR
# ============================================================

def execute_locator(
    district_name: str,
    coords: tuple,
    scheme_id: str = "MFS"
) -> str:

    if not partners_data:

        return (
            "Channel partner directory is currently "
            "unavailable. Please ensure "
            "data/odisha_partners.json exists."
        )


    scored = []


    for partner in partners_data:

        # Only actual partner records with
        # handles_schemes can be used here.

        if scheme_id not in partner.get(
            "handles_schemes",
            []
        ):

            continue


        try:

            partner_coords = (
                float(partner["lat"]),
                float(partner["lon"])
            )


            distance = geodesic(
                coords,
                partner_coords
            ).km


            scored.append(
                (
                    partner,
                    round(distance, 1)
                )
            )

        except (
            KeyError,
            TypeError,
            ValueError
        ):

            continue


    scored.sort(
        key=lambda item: item[1]
    )


    top_partners = scored[:3]


    if not top_partners:

        return (
            f"No eligible channel partners "
            f"were found near {district_name} "
            f"for the recommended scheme."
        )


    response = (
        f"### 📍 Nearest Channel Partners "
        f"near {district_name}\n\n"
    )


    for partner, distance in top_partners:

        response += (

            f"**🏦 {partner['name']}** "
            f"({partner['type']})\n\n"

            f"• District: "
            f"{partner['district']}\n\n"

            f"• Distance: "
            f"{distance} km\n\n"

            f"• Address: "
            f"{partner.get('address', 'N/A')}\n\n"

        )


    return response


# ============================================================
# INTENT ROUTER
# ============================================================

def process_message(
    prompt: str
) -> str:

    clean = prompt.lower().strip()


    cost = extract_cost(
        clean
    )


    district_info = extract_district(
        clean
    )


    # ========================================================
    # LOCATION REQUEST
    # ========================================================

    location_words = [
        "near",
        "nearest",
        "branch",
        "partner",
        "bank",
        "location",
        "locate",
        "where"
    ]


    if any(
        word in clean
        for word in location_words
    ):

        if district_info:

            st.session_state.pending_action = None

            return execute_locator(
                district_info[0],
                district_info[1]
            )


        st.session_state.pending_action = (
            "locator"
        )


        return (
            "Sure! I can help you find the "
            "nearest channel partner. "
            "Please tell me your district in Odisha."
        )


    # ========================================================
    # CONTINUE LOCATION CONVERSATION
    # ========================================================

    if (
        st.session_state.get(
            "pending_action"
        ) == "locator"
        and district_info
    ):

        st.session_state.pending_action = None

        return execute_locator(
            district_info[0],
            district_info[1]
        )


    # ========================================================
    # COST PROVIDED
    # ========================================================

    if cost is not None:

        st.session_state.pending_action = None


        purpose = extract_purpose(
            clean
        )


        return execute_scheme_and_emi(
            purpose,
            cost
        )


    # ========================================================
    # SCHEME / EMI REQUEST
    # ========================================================

    scheme_words = [
        "scheme",
        "emi",
        "calculate",
        "loan",
        "business",
        "project",
        "education",
        "student"
    ]


    if any(
        word in clean
        for word in scheme_words
    ):

        st.session_state.pending_action = (
            "scheme_calc"
        )


        purpose = extract_purpose(
            clean
        )


        if purpose == "education":

            return (
                "Sure! I can help you with the "
                "Educational Loan Scheme. "
                "Please tell me your estimated "
                "course/education cost."
            )


        return (
            "Sure! I can help you find the "
            "right loan scheme and estimate "
            "your EMI. Please tell me your "
            "estimated project cost, for example "
            "₹1.4 lakh or ₹500000."
        )


    # ========================================================
    # CONTINUE SCHEME CONVERSATION
    # ========================================================

    if (
        st.session_state.get(
            "pending_action"
        ) == "scheme_calc"
    ):

        return (
            "Please enter your estimated "
            "project/course cost, for example "
            "₹1 lakh, ₹2.5 lakh or ₹500000."
        )


    # ========================================================
    # GREETING
    # ========================================================

    if any(
        word in clean
        for word in [
            "hi",
            "hello",
            "hey",
            "namaste",
            "pranam"
        ]
    ):

        return (
            "Hello! 👋 I am your NSFDC Setu Guide.\n\n"
            "I can help you:\n\n"
            "• Find the right loan scheme\n"
            "• Estimate your EMI\n"
            "• Find a nearby channel partner\n\n"
            "What would you like help with?"
        )


    # ========================================================
    # NSFDC
    # ========================================================

    if (
        "nsfdc" in clean
        or "what is nsfdc" in clean
    ):

        return (
            "NSFDC stands for National Scheduled "
            "Castes Finance and Development "
            "Corporation. It provides concessional "
            "financial assistance through applicable "
            "schemes and channel partners."
        )


    # ========================================================
    # HELP
    # ========================================================

    if any(
        word in clean
        for word in [
            "help",
            "what can you do",
            "options"
        ]
    ):

        return (
            "I can help you with:\n\n"
            "1. 🏦 Find a suitable loan scheme\n"
            "2. 💰 Estimate your EMI\n"
            "3. 📍 Find a nearby channel partner\n\n"
            "Just tell me what you need."
        )


    # ========================================================
    # DEFAULT
    # ========================================================

    return (
        "I can help you find a suitable "
        "NSFDC scheme, estimate your EMI, "
        "or locate a nearby channel partner.\n\n"
        "For example, you can say:\n"
        "• I need a business loan\n"
        "• I need an education loan\n"
        "• My project costs ₹5 lakh\n"
        "• Find a bank near me"
    )