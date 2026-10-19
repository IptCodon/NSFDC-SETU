# ============================================================
# NSFDC SETU
# app.py
# ============================================================

import json
from pathlib import Path

import streamlit as st
import folium

from streamlit_folium import st_folium

from backend import (
    load_schemes,
    get_loan_estimate
)

from geo_locator import (
    load_partners,
    get_nearest_partner_results
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="NSFDC Setu Prototype",
    page_icon="🏦",
    layout="wide"
)


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"

SCHEMES_FILE = DATA_DIR / "schemes.json"

DISTRICTS_FILE = DATA_DIR / "districts.json"

PARTNERS_FILE = DATA_DIR / "odisha_partners.json"


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main {
        padding-top: 1rem;
        padding-bottom: 3rem;
    }

    .main-title {
        text-align: center;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }

    .subtitle {
        text-align: center;
        font-size: 1.15rem;
        margin-bottom: 1.5rem;
    }

    .section-title {
        font-size: 2rem;
        font-weight: 650;
        margin-top: 1.2rem;
        margin-bottom: 1rem;
    }

    .small-note {
        opacity: 0.75;
        font-size: 0.95rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOAD SCHEMES
# ============================================================

@st.cache_data
def get_schemes():

    return load_schemes(
        SCHEMES_FILE
    )


# ============================================================
# LOAD PARTNERS
# ============================================================

@st.cache_data
def get_partners():

    return load_partners(
        PARTNERS_FILE
    )


# ============================================================
# LOAD DISTRICTS
# ============================================================

@st.cache_data
def get_district_data():

    with open(
        DISTRICTS_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# LOAD ALL DATA
# ============================================================

try:

    schemes = get_schemes()

except Exception as e:

    st.error(
        f"Error loading schemes.json: {e}"
    )

    st.stop()


try:

    partners = get_partners()

except Exception as e:

    st.error(
        f"Error loading odisha_partners.json: {e}"
    )

    st.stop()


try:

    districts_data = get_district_data()

except Exception as e:

    st.error(
        f"Error loading districts.json: {e}"
    )

    st.stop()


# ============================================================
# DISTRICT NORMALIZATION
# ============================================================

def extract_districts(data):

    # --------------------------------------------------------
    # FORMAT:
    #
    # [
    #   {
    #       "district": "Angul",
    #       "lat": 20.84,
    #       "lon": 85.10
    #   }
    # ]
    # --------------------------------------------------------

    if isinstance(data, list):

        return data


    # --------------------------------------------------------
    # FORMAT:
    #
    # {
    #     "districts": [...]
    # }
    # --------------------------------------------------------

    if isinstance(data, dict):

        if "districts" in data:

            return data["districts"]


        # ----------------------------------------------------
        # FORMAT:
        #
        # {
        #     "Angul": {
        #         "lat": ...,
        #         "lon": ...
        #     }
        # }
        # ----------------------------------------------------

        result = []

        for name, value in data.items():

            if isinstance(
                value,
                dict
            ):

                item = dict(value)

                item[
                    "district"
                ] = name

                result.append(
                    item
                )

        return result


    return []


district_records = extract_districts(
    districts_data
)


# ============================================================
# FALLBACK DISTRICT COORDINATES
# ============================================================

FALLBACK_DISTRICT_COORDS = {

    "Angul": (
        20.8442,
        85.1511
    ),

    "Bargarh": (
        21.3330,
        83.6190
    ),

    "Balangir": (
        20.7074,
        83.4840
    ),

    "Boudh": (
        20.8368,
        84.3262
    ),

    "Bhubaneswar": (
        20.2961,
        85.8245
    ),

    "Cuttack": (
        20.4625,
        85.8828
    ),

    "Jajpur": (
        20.8480,
        86.3376
    ),

    "Rayagada": (
        19.1716,
        83.4163
    ),

    "Rourkela": (
        22.2604,
        84.8536
    ),

    "Sambalpur": (
        21.4669,
        83.9756
    )

}


# ============================================================
# GET DISTRICT COORDINATES
# ============================================================

def get_district_coordinates(
    district_name
):

    target = str(
        district_name
    ).strip().lower()


    # First use districts.json

    for district in district_records:

        if not isinstance(
            district,
            dict
        ):

            continue


        name = (

            district.get(
                "district"
            )

            or

            district.get(
                "name"
            )

        )


        if not name:

            continue


        if (
            str(name)
            .strip()
            .lower()
            != target
        ):

            continue


        lat = (

            district.get(
                "lat"
            )

            if district.get(
                "lat"
            ) is not None

            else

            district.get(
                "latitude"
            )

        )


        lon = (

            district.get(
                "lon"
            )

            if district.get(
                "lon"
            ) is not None

            else

            district.get(
                "longitude"
            )

        )


        try:

            return (
                float(lat),
                float(lon)
            )

        except (
            TypeError,
            ValueError
        ):

            return None


    # Fallback

    for name, coords in (
        FALLBACK_DISTRICT_COORDS.items()
    ):

        if (
            name.lower()
            == target
        ):

            return coords


    return None


# ============================================================
# SCHEME HELPERS
# ============================================================

def scheme_id(
    scheme
):

    return str(

        scheme.get(
            "scheme_id"
        )

        or

        scheme.get(
            "id"
        )

        or

        ""

    ).strip()


def scheme_name(
    scheme
):

    return (

        scheme.get(
            "name"
        )

        or

        scheme.get(
            "scheme_name"
        )

        or

        "Unnamed Scheme"

    )


# ============================================================
# BUILD SCHEME DROPDOWN
# ============================================================

scheme_options = [
    "Choose"
]

scheme_lookup = {}


for scheme in schemes:

    sid = scheme_id(
        scheme
    )

    sname = scheme_name(
        scheme
    )


    if not sid:

        continue


    label = (
        f"{sname} ({sid})"
    )


    scheme_options.append(
        label
    )


    scheme_lookup[
        label
    ] = scheme


# ============================================================
# BUILD DISTRICT DROPDOWN
# ============================================================

district_names = []


for district in district_records:

    if not isinstance(
        district,
        dict
    ):

        continue


    name = (

        district.get(
            "district"
        )

        or

        district.get(
            "name"
        )

    )


    if name:

        district_names.append(
            str(name)
        )


# Add fallback districts

for district in (
    FALLBACK_DISTRICT_COORDS
):

    if district not in district_names:

        district_names.append(
            district
        )


district_names = sorted(
    set(district_names)
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="main-title">
        🏦 NSFDC Setu
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
        Your pathway to the right financial support
    </div>
    """,
    unsafe_allow_html=True
)

st.write(
    "Find the right NSFDC scheme, calculate your EMI, "
    "and locate your nearest channel partner."
)

st.divider()


# ============================================================
# NAVIGATION
# ============================================================

page = st.radio(

    "Navigation",

    [
        "🏦 Find My Scheme",
        "🤖 Chatbot",
        "📍 Find Partner"
    ],

    horizontal=True,

    label_visibility="collapsed"

)


# ============================================================
# ============================================================
# FIND MY SCHEME
# ============================================================
# ============================================================

if page == "🏦 Find My Scheme":

    # --------------------------------------------------------
    # Clear partner state when leaving partner page
    # --------------------------------------------------------

    if st.session_state.get(
        "current_page"
    ) != "scheme":

        st.session_state.pop(
            "partner_result",
            None
        )

        st.session_state.pop(
            "partner_search_location",
            None
        )

        st.session_state[
            "current_page"
        ] = "scheme"


    st.markdown(
        '<div class="section-title">'
        '👤 Tell us about yourself'
        '</div>',
        unsafe_allow_html=True
    )


    # ========================================================
    # PURPOSE
    # ========================================================

    purpose = st.selectbox(

        "What is this loan for?",

        [
            "Choose",
            "Business / Project",
            "Education"
        ],

        index=0,

        key="purpose_select"

    )


    if purpose == "Business / Project":

        st.info(
            "Business / Project\n\n"
            "Choose this option if you need financial "
            "assistance for an eligible income-generating "
            "activity, business or project."
        )


    elif purpose == "Education":

        st.info(
            "Education\n\n"
            "Choose this option if the financial assistance "
            "is required for an eligible education or "
            "professional course."
        )


    # ========================================================
    # PROJECT COST
    # ========================================================

    project_cost = st.number_input(

        "Estimated Project / Course Cost (₹)",

        min_value=0.0,

        value=0.0,

        step=1000.0,

        format="%.2f",

        key="project_cost_input"

    )


    st.markdown(

        '<div class="small-note">'
        'Enter the total estimated cost in rupees. '
        'Example: ₹5 lakh → enter 500000.'
        '</div>',

        unsafe_allow_html=True

    )


    # ========================================================
    # DISTRICT
    # ========================================================

    district = st.selectbox(

        "Your District",

        [
            "Choose"
        ] + district_names,

        index=0,

        key="scheme_district_select"

    )


    # ========================================================
    # FIND SCHEME BUTTON
    # ========================================================

    find_scheme = st.button(

        "🔍 Find My Scheme",

        type="primary",

        use_container_width=True,

        key="find_scheme_button"

    )


    # ========================================================
    # FIND SCHEME
    # ========================================================

    if find_scheme:

        # Clear previous result

        st.session_state.pop(
            "scheme_result",
            None
        )


        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        errors = []


        if purpose == "Choose":

            errors.append(
                "Please choose what the loan is for."
            )


        if project_cost <= 0:

            errors.append(
                "Please enter the estimated "
                "project/course cost."
            )


        if district == "Choose":

            errors.append(
                "Please select your district."
            )


        # ----------------------------------------------------
        # SHOW ERRORS
        # ----------------------------------------------------

        if errors:

            for error in errors:

                st.error(
                    error
                )


        # ----------------------------------------------------
        # PROCESS
        # ----------------------------------------------------

        else:

            user_profile = {

                "purpose":
                    purpose,

                "project_cost":
                    project_cost,

                "district":
                    district

            }


            try:

                result = get_loan_estimate(

                    user_profile,

                    schemes

                )


            except Exception as e:

                st.error(
                    f"Unable to calculate recommendation: {e}"
                )

                result = None


            if result:

                if result.get(
                    "success",
                    False
                ):

                    st.session_state[
                        "scheme_result"
                    ] = result

                else:

                    st.error(

                        result.get(
                            "message",
                            "No suitable scheme found."
                        )

                    )


    # ========================================================
    # DISPLAY SCHEME RESULT
    # ========================================================

    if (
        "scheme_result"
        in st.session_state
    ):

        result = st.session_state[
            "scheme_result"
        ]


        st.divider()


        st.markdown(
            '<div class="section-title">'
            '✅ Recommended for you'
            '</div>',
            unsafe_allow_html=True
        )


        st.markdown(
            f"## 🏦 {result.get('scheme_name', 'Recommended Scheme')}"
        )


        if result.get(
            "description"
        ):

            st.write(
                result[
                    "description"
                ]
            )


        # ====================================================
        # FIND FULL SCHEME DATA
        # ====================================================

        result_scheme_id = str(
            result.get(
                "scheme_id",
                ""
            )
        )


        selected_scheme = None


        for scheme in schemes:

            if (
                scheme_id(
                    scheme
                )
                == result_scheme_id
            ):

                selected_scheme = scheme

                break


        # ====================================================
        # WHAT TO DO
        # ====================================================

        if selected_scheme:

            what_to_do = selected_scheme.get(
                "what_to_do"
            )


            eligibility = selected_scheme.get(
                "eligibility"
            )


            documents = selected_scheme.get(
                "documents_required"
            )


            application_steps = selected_scheme.get(
                "application_steps"
            )


            # ------------------------------------------------
            # WHAT TO DO
            # ------------------------------------------------

            if what_to_do:

                st.markdown(
                    "### 📝 What can you do with this scheme?"
                )

                st.write(
                    what_to_do
                )


            # ------------------------------------------------
            # ELIGIBILITY
            # ------------------------------------------------

            if eligibility:

                st.markdown(
                    "### 👥 Who can apply?"
                )


                if isinstance(
                    eligibility,
                    list
                ):

                    for item in eligibility:

                        st.write(
                            f"• {item}"
                        )

                else:

                    st.write(
                        eligibility
                    )


            # ------------------------------------------------
            # DOCUMENTS
            # ------------------------------------------------

            if documents:

                st.markdown(
                    "### 📄 Documents you may need"
                )


                if isinstance(
                    documents,
                    list
                ):

                    for item in documents:

                        st.write(
                            f"• {item}"
                        )

                else:

                    st.write(
                        documents
                    )


            # ------------------------------------------------
            # APPLICATION
            # ------------------------------------------------

            if application_steps:

                st.markdown(
                    "### 🚶 How to apply"
                )


                if isinstance(
                    application_steps,
                    list
                ):

                    for i, step in enumerate(

                        application_steps,

                        start=1

                    ):

                        st.write(
                            f"{i}. {step}"
                        )

                else:

                    st.write(
                        application_steps
                    )


        # ====================================================
        # SCHEME METRICS
        # ====================================================

        col1, col2 = st.columns(2)


        with col1:

            st.metric(

                "Interest Rate",

                f"{result.get('interest_rate', '—')}%"

            )


        with col2:

            st.metric(

                "Maximum Tenure",

                f"{result.get('max_tenure_years', '—')} years"

            )


        st.success(
            "This scheme matches the information "
            "you provided."
        )


        # ====================================================
        # EMI
        # ====================================================

        if result.get(
            "emi_details"
        ):

            st.divider()


            st.markdown(
                '<div class="section-title">'
                '💰 Estimated EMI'
                '</div>',
                unsafe_allow_html=True
            )


            emi = result[
                "emi_details"
            ]


            st.metric(

                "Estimated Monthly EMI",

                f"₹{emi.get('emi', 0):,.0f}"

            )


            col1, col2, col3 = st.columns(3)


            with col1:

                st.write(
                    "**Loan Amount**"
                )

                st.write(
                    f"₹{emi.get('loan_amount', 0):,.0f}"
                )


            with col2:

                st.write(
                    "**Interest Rate**"
                )

                st.write(
                    f"{emi.get('interest_rate', 0)}%"
                )


            with col3:

                st.write(
                    "**Tenure**"
                )

                st.write(
                    f"{emi.get('tenure_years', 0)} years"
                )


            if result.get(
                "moratorium_note"
            ):

                st.info(
                    result[
                        "moratorium_note"
                    ]
                )


            if result.get(
                "emi_note"
            ):

                st.caption(
                    result[
                        "emi_note"
                    ]
                )


# ============================================================
# ============================================================
# CHATBOT
# ============================================================
# ============================================================

elif page == "🤖 Chatbot":

    # --------------------------------------------------------
    # Clear partner state
    # --------------------------------------------------------

    if st.session_state.get(
        "current_page"
    ) != "chatbot":

        st.session_state.pop(
            "partner_result",
            None
        )

        st.session_state.pop(
            "partner_search_location",
            None
        )

        st.session_state[
            "current_page"
        ] = "chatbot"


    st.markdown(
        '<div class="section-title">'
        '🤖 NSFDC Setu Assistant'
        '</div>',
        unsafe_allow_html=True
    )


    st.write(
        "Ask questions about NSFDC schemes, eligibility, "
        "documents, EMI or the application process."
    )


    # ========================================================
    # CHATBOT IMPORT
    # ========================================================

    try:

        from chatbot import (
            get_chatbot_response
        )

    except ImportError:

        get_chatbot_response = None


    # ========================================================
    # CHAT HISTORY
    # ========================================================

    if "messages" not in st.session_state:

        st.session_state[
            "messages"
        ] = []


    # ========================================================
    # DISPLAY CHAT
    # ========================================================

    for message in st.session_state[
        "messages"
    ]:

        with st.chat_message(
            message["role"]
        ):

            st.write(
                message["content"]
            )


    # ========================================================
    # USER INPUT
    # ========================================================

    user_message = st.chat_input(
        "Ask NSFDC Setu..."
    )


    if user_message:

        # ----------------------------------------------------
        # USER MESSAGE
        # ----------------------------------------------------

        st.session_state[
            "messages"
        ].append({

            "role":
                "user",

            "content":
                user_message

        })


        with st.chat_message(
            "user"
        ):

            st.write(
                user_message
            )


        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        if get_chatbot_response:

            try:

                response = (
                    get_chatbot_response(
                        user_message
                    )
                )

            except TypeError:

                try:

                    response = (
                        get_chatbot_response(
                            user_message,
                            schemes
                        )
                    )

                except Exception as e:

                    response = (
                        "I couldn't process that question "
                        f"right now. {e}"
                    )

            except Exception as e:

                response = (
                    "I couldn't process that question "
                    f"right now. {e}"
                )

        else:

            response = (
                "The chatbot module is not available. "
                "Please make sure chatbot.py is present "
                "in the project folder."
            )


        # ----------------------------------------------------
        # HANDLE DICTIONARY RESPONSE
        # ----------------------------------------------------

        if isinstance(
            response,
            dict
        ):

            response = (

                response.get(
                    "response"
                )

                or

                response.get(
                    "message"
                )

                or

                str(response)

            )


        # ----------------------------------------------------
        # ASSISTANT MESSAGE
        # ----------------------------------------------------

        with st.chat_message(
            "assistant"
        ):

            st.write(
                response
            )


        st.session_state[
            "messages"
        ].append({

            "role":
                "assistant",

            "content":
                response

        })


# ============================================================
# ============================================================
# FIND PARTNER
# ============================================================
# ============================================================

elif page == "📍 Find Partner":

    # --------------------------------------------------------
    # CLEAR RESULT WHEN ENTERING PAGE
    # --------------------------------------------------------

    if st.session_state.get(
        "current_page"
    ) != "partner":

        st.session_state.pop(
            "partner_result",
            None
        )

        st.session_state.pop(
            "partner_search_location",
            None
        )

        st.session_state[
            "current_page"
        ] = "partner"


    st.markdown(
        '<div class="section-title">'
        '📍 Find Nearby Channel Partner'
        '</div>',
        unsafe_allow_html=True
    )


    st.write(
        "Choose a scheme and your district to find "
        "nearby eligible channel partners."
    )


    # ========================================================
    # SCHEME DROPDOWN
    # ========================================================

    selected_scheme_label = st.selectbox(

        "Select Scheme",

        scheme_options,

        index=0,

        key="partner_scheme"

    )


    # ========================================================
    # DISTRICT DROPDOWN
    # ========================================================

    selected_partner_district = st.selectbox(

        "Select District",

        [
            "Choose"
        ] + district_names,

        index=0,

        key="partner_district"

    )


    # ========================================================
    # FIND PARTNER BUTTON
    # ========================================================

    find_partners = st.button(

        "📍 Find Nearby Partners",

        type="primary",

        use_container_width=True,

        key="partner_button"

    )


    # ========================================================
    # SEARCH
    # ========================================================

    if find_partners:

        # Clear old result FIRST

        st.session_state.pop(
            "partner_result",
            None
        )

        st.session_state.pop(
            "partner_search_location",
            None
        )


        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if selected_scheme_label == "Choose":

            st.error(
                "Please select a scheme."
            )


        elif selected_partner_district == "Choose":

            st.error(
                "Please select a district."
            )


        else:

            # ------------------------------------------------
            # GET SCHEME
            # ------------------------------------------------

            selected_scheme = (
                scheme_lookup[
                    selected_scheme_label
                ]
            )


            selected_scheme_id = scheme_id(
                selected_scheme
            )


            # ------------------------------------------------
            # GET DISTRICT COORDINATES
            # ------------------------------------------------

            coordinates = (
                get_district_coordinates(
                    selected_partner_district
                )
            )


            if not coordinates:

                st.error(
                    "Coordinates for this district "
                    "could not be found."
                )


            else:

                user_lat, user_lon = coordinates


                # ------------------------------------------------
                # FIND NEAREST PARTNERS
                # ------------------------------------------------

                try:

                    partner_result = (
                        get_nearest_partner_results(

                            user_lat,

                            user_lon,

                            selected_scheme_id,

                            partners,

                            top_n=5

                        )
                    )


                except Exception as e:

                    st.error(
                        f"Partner search failed: {e}"
                    )

                    partner_result = None


                # ------------------------------------------------
                # SAVE RESULT
                # ------------------------------------------------

                if partner_result is not None:

                    st.session_state[
                        "partner_result"
                    ] = partner_result

                    st.session_state[
                        "partner_search_location"
                    ] = (

                        selected_partner_district,

                        user_lat,

                        user_lon

                    )


    # ========================================================
    # DISPLAY RESULT
    # ========================================================

    if (
        "partner_result"
        in st.session_state
    ):

        partner_result = (
            st.session_state[
                "partner_result"
            ]
        )


        st.divider()


        # ====================================================
        # NO PARTNERS
        # ====================================================

        if not partner_result.get(
            "partners"
        ):

            st.warning(
                "No channel partners handling this "
                "scheme were found in the loaded dataset."
            )


            st.info(
                "Add a partner with the selected scheme ID "
                "to odisha_partners.json and it will become "
                "available here."
            )


        # ====================================================
        # PARTNERS FOUND
        # ====================================================

        else:

            # =================================================
            # MAP
            # =================================================

            st.markdown(
                "### 🗺️ Partner Locations"
            )


            search_location = (
                st.session_state.get(
                    "partner_search_location"
                )
            )


            if search_location:

                (
                    district_name,
                    user_lat,
                    user_lon
                ) = search_location


                partner_map = folium.Map(

                    location=[
                        user_lat,
                        user_lon
                    ],

                    zoom_start=8

                )


                # ------------------------------------------------
                # SELECTED DISTRICT
                # ------------------------------------------------

                folium.Marker(

                    [
                        user_lat,
                        user_lon
                    ],

                    tooltip=(
                        f"Selected district: "
                        f"{district_name}"
                    ),

                    popup=(
                        f"<b>Selected District</b><br>"
                        f"{district_name}"
                    ),

                    icon=folium.Icon(
                        color="red",
                        icon="home"
                    )

                ).add_to(
                    partner_map
                )


                # ------------------------------------------------
                # PARTNER MARKERS
                # ------------------------------------------------

                for index, partner in enumerate(

                    partner_result[
                        "partners"
                    ],

                    start=1

                ):

                    try:

                        plat = float(
                            partner.get(
                                "lat"
                            )
                        )

                        plon = float(
                            partner.get(
                                "lon"
                            )
                        )

                    except (
                        TypeError,
                        ValueError
                    ):

                        continue


                    partner_name = (

                        partner.get(
                            "name"
                        )

                        or

                        partner.get(
                            "partner_name"
                        )

                        or

                        "Channel Partner"

                    )


                    partner_type = (

                        partner.get(
                            "type"
                        )

                        or

                        partner.get(
                            "partner_type"
                        )

                        or

                        "Channel Partner"

                    )


                    distance = float(

                        partner.get(
                            "distance_km",
                            0
                        )

                    )


                    popup = (

                        f"<b>{index}. "
                        f"{partner_name}</b><br>"
                        f"Type: {partner_type}<br>"
                        f"Distance: "
                        f"{distance:.1f} km"

                    )


                    folium.Marker(

                        [
                            plat,
                            plon
                        ],

                        tooltip=(
                            f"{index}. "
                            f"{partner_name}"
                        ),

                        popup=popup,

                        icon=folium.Icon(
                            color="blue",
                            icon="bank"
                        )

                    ).add_to(
                        partner_map
                    )


                st_folium(

                    partner_map,

                    width=None,

                    height=500

                )


            # =================================================
            # PARTNER LIST
            # =================================================

            st.markdown(
                "### 🏦 Available Partners"
            )


            for index, partner in enumerate(

                partner_result[
                    "partners"
                ],

                start=1

            ):

                partner_name = (

                    partner.get(
                        "name"
                    )

                    or

                    partner.get(
                        "partner_name"
                    )

                    or

                    "Channel Partner"

                )


                partner_type = (

                    partner.get(
                        "type"
                    )

                    or

                    partner.get(
                        "partner_type"
                    )

                    or

                    "Channel Partner"

                )


                distance = float(

                    partner.get(
                        "distance_km",
                        0
                    )

                )


                st.markdown(
                    f"## {index}. 🏦 {partner_name}"
                )


                col1, col2 = st.columns(2)


                with col1:

                    st.write(
                        f"**Type:** {partner_type}"
                    )


                with col2:

                    st.write(
                        f"**Distance:** "
                        f"{distance:.1f} km"
                    )


                st.success(
                    "Eligible channel partner for "
                    "the selected scheme."
                )


                address = partner.get(
                    "address"
                )


                phone = partner.get(
                    "phone"
                )


                if address:

                    st.write(
                        f"📍 **Address:** {address}"
                    )


                if phone:

                    st.write(
                        f"📞 **Phone:** {phone}"
                    )


                st.divider()


# ============================================================
# FOOTER
# ============================================================

st.caption(
    "NSFDC Setu • SIH Prototype"
)