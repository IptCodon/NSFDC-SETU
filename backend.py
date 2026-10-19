# ============================================================
# NSFDC SETU
# BACKEND
# ============================================================

import json
from pathlib import Path


# ============================================================
# LOAD SCHEMES
# ============================================================

def load_schemes(file_path):
    """
    Load schemes from schemes.json.
    """

    file_path = Path(file_path)

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        schemes = json.load(file)

    if not isinstance(schemes, list):

        raise ValueError(
            "schemes.json must contain a list."
        )

    return schemes


# ============================================================
# FIND SUITABLE SCHEMES
# ============================================================

def find_suitable_schemes(
    purpose,
    project_cost,
    schemes
):

    purpose = str(
        purpose
    ).lower().strip()


    project_cost = float(
        project_cost
    )


    suitable = []


    for scheme in schemes:

        scheme_purpose = str(
            scheme.get(
                "purpose",
                ""
            )
        ).lower().strip()


        # ----------------------------------------------------
        # PURPOSE MATCH
        # ----------------------------------------------------

        if scheme_purpose != purpose:

            continue


        # ----------------------------------------------------
        # FUNDING LIMIT
        # ----------------------------------------------------

        max_loan_amount = float(

            scheme.get(
                "max_loan_amount",
                0
            )

        )


        funding_percentage = float(

            scheme.get(
                "max_loan_pct_of_cost",
                100
            )

        )


        # ----------------------------------------------------
        # CALCULATE ELIGIBLE LOAN
        # ----------------------------------------------------

        loan_based_on_cost = (

            project_cost
            * funding_percentage
            / 100

        )


        estimated_loan = min(

            loan_based_on_cost,

            max_loan_amount

        )


        if estimated_loan <= 0:

            continue


        # ----------------------------------------------------
        # COPY SCHEME
        # ----------------------------------------------------

        scheme_result = dict(
            scheme
        )


        scheme_result[
            "estimated_loan_amount"
        ] = estimated_loan


        suitable.append(
            scheme_result
        )


    return suitable


# ============================================================
# EMI CALCULATOR
# ============================================================

def calculate_emi(
    principal,
    annual_interest_rate,
    tenure_years
):

    principal = float(
        principal
    )

    annual_interest_rate = float(
        annual_interest_rate
    )

    tenure_years = float(
        tenure_years
    )


    if principal <= 0:

        return 0


    if tenure_years <= 0:

        return 0


    monthly_rate = (

        annual_interest_rate
        / 100
        / 12

    )


    total_months = int(

        tenure_years
        * 12

    )


    # --------------------------------------------------------
    # ZERO INTEREST
    # --------------------------------------------------------

    if monthly_rate == 0:

        return (

            principal
            / total_months

        )


    # --------------------------------------------------------
    # EMI FORMULA
    # --------------------------------------------------------

    emi = (

        principal
        * monthly_rate
        * (
            1 + monthly_rate
        ) ** total_months

    ) / (

        (
            1 + monthly_rate
        ) ** total_months
        - 1

    )


    return emi


# ============================================================
# MAIN LOAN ESTIMATE
# ============================================================

def get_loan_estimate(
    profile,
    schemes
):

    # ========================================================
    # GET USER INPUT
    # ========================================================

    purpose = profile.get(
        "purpose"
    )


    project_cost = profile.get(
        "project_cost"
    )


    # ========================================================
    # VALIDATE PURPOSE
    # ========================================================

    if not purpose:

        return {

            "success": False,

            "message":
                "Loan purpose was not provided."

        }


    # ========================================================
    # VALIDATE COST
    # ========================================================

    try:

        project_cost = float(
            project_cost
        )

    except (
        TypeError,
        ValueError
    ):

        return {

            "success": False,

            "message":
                "Please enter a valid project/course cost."

        }


    if project_cost <= 0:

        return {

            "success": False,

            "message":
                "Project/course cost must be greater than zero."

        }


    # ========================================================
    # FIND MATCHING SCHEMES
    # ========================================================

    suitable_schemes = find_suitable_schemes(

        purpose=
            purpose,

        project_cost=
            project_cost,

        schemes=
            schemes

    )


    # ========================================================
    # NO SCHEME
    # ========================================================

    if not suitable_schemes:

        return {

            "success": False,

            "message":
                "No suitable scheme was found for "
                "the information provided."

        }


    # ========================================================
    # SELECT FIRST MATCH
    # ========================================================

    scheme = suitable_schemes[0]


    # ========================================================
    # SCHEME DETAILS
    # ========================================================

    scheme_id = scheme.get(
        "scheme_id",
        ""
    )


    scheme_name = scheme.get(
        "name",
        "Recommended Scheme"
    )


    description = scheme.get(
        "description",
        ""
    )


    # ========================================================
    # LOAN AMOUNT
    # ========================================================

    loan_amount = float(

        scheme.get(
            "estimated_loan_amount",
            0
        )

    )


    scheme_max_loan = float(

        scheme.get(
            "max_loan_amount",
            0
        )

    )


    # ========================================================
    # INTEREST
    # ========================================================

    interest_rate = float(

        scheme.get(
            "interest_rate_beneficiary",
            0
        )

    )


    # ========================================================
    # TENURE
    # ========================================================

    tenure_years = float(

        scheme.get(
            "max_tenure_years",
            0
        )

    )


    # ========================================================
    # MORATORIUM
    # ========================================================

    moratorium_months = int(

        scheme.get(
            "moratorium_months",
            0
        )

    )


    # ========================================================
    # EMI
    # ========================================================

    emi = calculate_emi(

        principal=
            loan_amount,

        annual_interest_rate=
            interest_rate,

        tenure_years=
            tenure_years

    )


    # ========================================================
    # EMI DETAILS
    # ========================================================

    emi_details = {

        "loan_amount":
            loan_amount,

        "interest_rate":
            interest_rate,

        "tenure_years":
            tenure_years,

        "emi":
            emi

    }


    # ========================================================
    # MORATORIUM MESSAGE
    # ========================================================

    if moratorium_months > 0:

        moratorium_note = (

            f"Moratorium considered: "
            f"{moratorium_months} months. "
            "Actual repayment terms may vary "
            "based on the applicable scheme and lender."

        )

    else:

        moratorium_note = (
            "No moratorium has been included "
            "in this estimate."
        )


    # ========================================================
    # EMI NOTE
    # ========================================================

    emi_note = (

        "This is an estimated EMI based on the "
        "selected scheme's interest rate and "
        "maximum tenure. Final repayment terms "
        "may vary."

    )


    # ========================================================
    # RETURN RESULT
    # ========================================================

    return {

        "success":
            True,

        "scheme_id":
            scheme_id,

        "scheme_name":
            scheme_name,

        "description":
            description,

        "project_cost":
            project_cost,

        "max_loan_amount":
            loan_amount,

        "scheme_max_loan_amount":
            scheme_max_loan,

        "interest_rate":
            interest_rate,

        "max_tenure_years":
            tenure_years,

        "selected_moratorium_months":
            moratorium_months,

        "emi_details":
            emi_details,

        "moratorium_note":
            moratorium_note,

        "emi_note":
            emi_note,

        "source":
            scheme.get(
                "source",
                ""
            ),

        "last_verified":
            scheme.get(
                "last_verified",
                ""
            )

    }