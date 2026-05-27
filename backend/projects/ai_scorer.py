import os
import json
import re
import importlib
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"

if load_dotenv is not None:
    load_dotenv(ENV_PATH)

# Groq API Key. Keep the actual key in backend/.env:
# GROQ_API_KEY=your_groq_api_key
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")


def get_groq_api_key() -> str:
    if load_dotenv is not None:
        load_dotenv(ENV_PATH)
    return os.environ.get("GROQ_API_KEY", "").strip()

NEGATIVE_KEYWORDS = {
    "administrative": 25,
    "support to operations": 25,
    "guarantee": 30,
    "private institution": 30,
    "private sector": 30,
    "right-sizing": 25,
    "rightsizing": 25,
    "organization unit": 25,
    "organizational unit": 25,
    "office establishment": 25,
    "reorganization": 25,
    "masterplan": 20,
    "master plan": 20,
    "roadmap": 20,
    "issp": 20,
    "ict expenses": 20,
    "operating ict": 20,
    "continuing ict": 20,
    "preparatory": 20,
    "rap": 20,
    "rowa": 20,
    "pre-fs": 20,
    "pre-feasibility": 20,
    "feasibility study": 20,
    "ded": 20,
    "detailed engineering design": 20,
    "funding facility": 25,
    "funding facilities": 25,
    "acquisition of lots": 35,
    "lot acquisition": 35,
    "single unit": 30,
    "maintenance": 20,
    "landscaping": 25,
    "site development": 25,
    "perimeter fence": 25,
    "non-infrastructure": 25,
    "non infrastructure": 25,
    "government building": 20,
    "expanded pdp": 20,
}

POSITIVE_KEYWORDS = {
    "health": 15,
    "education": 15,
    "livelihood": 15,
    "disaster": 20,
    "climate": 15,
    "flood control": 20,
    "public safety": 15,
    "water supply": 15,
    "sanitation": 15,
    "transport": 15,
    "digital service": 15,
    "transparency": 15,
    "accountability": 15,
    "public service": 15,
}

SECTOR_PRIORITIZATION_CRITERIA = """
Sector Prioritization Criteria for Projects and Programs:

Common project/program criteria, subtotal 50%:
- Readiness, 20%:
  - 10: With completed documents such as pre-FS/FS/POW and detailed design, where applicable.
  - 6: Ongoing pre-FS/FS/POW and detailed design, where applicable.
  - 3: With Comprehensive Project Profile.
  - 0: With concept paper only or none.
- Level of GAD Responsiveness, 15%:
  - 10: Program/project is gender-responsive.
  - 6: Program/project is gender-sensitive.
  - 3: Program/project has promising GAD prospects.
  - 0: GAD is invisible in the program/project.
- Spatial Coverage, 15%:
  - 10: Region-wide or interregional.
  - 6: 6 to 12 cities/municipalities.
  - 3: 1 to 5 cities/municipalities.
  - 0: None.

RDP Sectoral Outcomes, subtotal 50%. Apply only the criteria group for the assigned Sectoral Committee:
- Economic sector:
  - Develop and protect capabilities of individuals and families, 10%.
  - Transform production sector to generate more quality jobs and competitive products, 5%.
  - Modernize agriculture and agri-business, 5%.
  - Revitalize industry and reinvigorate services, 20%.
  - Promote trade and investment and advance R&D, technology, and innovation, 10%.
- Environment sector:
  - Develop and protect capabilities of individuals and families, 10%.
  - Transform production sector to generate more quality jobs and competitive products, 5%.
  - Establish livable communities, 10%.
  - Climate change adaptation and mitigation, 15%.
  - Disaster preparedness, relief, recovery, and reconstruction, 10%.
- Infrastructure sector:
  - Develop and protect capabilities of individuals and families, 10%.
  - Transform production sector to generate more quality jobs and competitive products, 5%.
  - Achieve seamless and inclusive connectivity, 20%.
  - Upgrade and enhance infrastructure for sustainable energy and water system, 10%.
  - Provide enhanced support to social development, 5%.
- Financial and Development Administration sector:
  - Develop and protect capabilities of individuals and families, 10%.
  - Transform production sector to generate more quality jobs and competitive products, 5%.
  - Promote financial inclusion and improve public financial management, 5%.
  - Promote culture-sensitive governance and development, 10%.
  - Ensure peace and security, and enhance administration of justice, 20%.
- Social sector:
  - Develop and protect capabilities of individuals and families, 10%.
  - Transform production sector to generate more quality jobs and competitive products, 5%.
  - Promote human and social development, 20%.
  - Reduce vulnerabilities and protect purchasing power, 10%.
  - Increase income-earning ability, 5%.

Scoring for each sector criterion:
- 10: Strongly agree.
- 8: Agree.
- 5: Neutral.
- 3: Disagree.
- 0: Strongly disagree.
""".strip()

REGIONAL_PRIORITIZATION_CRITERIA = """
Regional Prioritization Criteria:
- Use this only when the project/program cost is PHP 200 million or above.
- If the budget is less than PHP 200 million, classify it under the "Sectoral Projects" list and do not apply the Regional Prioritization Criteria.

Regional project cost, 25%:
- 10: PHP 5 billion and above.
- 8: Above PHP 3 billion to less than PHP 5 billion.
- 6: Above PHP 1 billion to PHP 3 billion.
- 4: Above PHP 500 million to PHP 1 billion.
- 2: PHP 200 million to PHP 500 million.

Spatial coverage, 25%:
- 10: Interregional.
- 8: Regionwide.
- 6: 8 to 12 cities or municipalities.
- 4: City or municipality alone.

Contribution to Regional Development Plan (RDP) sectoral outcome, 25%:
- 10: Contributing to 7 or more RDP outcomes.
- 8: Contributing to 5 to 6 RDP outcomes.
- 6: Contributing to 3 to 4 RDP outcomes.
- 4: Contributing to 2 RDP outcomes.
- 2: Contributing to 1 RDP outcome.

Magnitude of beneficiaries, 25%:
- 10: Above 3 million population.
- 6: Above 1 million to 3 million population.
- 3: 1 person to 1 million population.
""".strip()

NEGATIVE_LIST_CRITERIA = [
    "Recurrent/non-recurrent spending for general administrative and support to operations of agencies",
    "Guarantee-related activities to private institutions",
    "PAPs to be financed purely from LGU funds and independent projects of the private sector",
    "Creation/establishment of an office or organizational unit, right-sizing, and other reorganization-related activities",
    "Formulation/preparation of roadmap, masterplan, ISSP of implementing agencies, including continuing or operating ICT expenses",
    "Stand-alone preparatory activities for infrastructure PAPs (RAP, ROWA, pre-FS, FS, DED)",
    "Funding facilities managed by implementing agencies as part of their regular program/mandate",
    "Acquisition of lots",
    "Construction, improvement, rehabilitation, restoration, or maintenance of a single unit of a building/structure",
    "Landscaping, site development, installation of perimeter fence, or similar non-infrastructure items",
    "Government buildings that are not responsive to the outcome and indicator statements in the Expanded PDP 2023-2028 RM",
]


def normalize(text):
    return re.sub(r"\s+", " ", text.lower()).strip()


def flatten_profile_data(value: Any, prefix: str = "") -> List[str]:
    if value in (None, ""):
        return []
    if isinstance(value, dict):
        lines = []
        for key, child in value.items():
            if key == "simplified_form_meta":
                continue
            label = f"{prefix}.{key}" if prefix else str(key)
            lines.extend(flatten_profile_data(child, label))
        return lines
    if isinstance(value, list):
        lines = []
        for index, child in enumerate(value, 1):
            label = f"{prefix}[{index}]" if prefix else f"item_{index}"
            lines.extend(flatten_profile_data(child, label))
        return lines
    return [f"{prefix}: {value}" if prefix else str(value)]


def build_form_text(title: str, description: str = "", profile_data: Optional[Dict[str, Any]] = None) -> str:
    lines = [f"Project Name: {title}"]
    if description:
        lines.append(f"Description: {description}")
    if isinstance(profile_data, dict):
        profile_lines = flatten_profile_data(profile_data)
        if profile_lines:
            lines.append("Project Profile Data:")
            lines.extend(profile_lines)
    return "\n".join(lines)


def build_prompt(form_text: str) -> List[Dict[str, str]]:
    system_prompt = f"""
You are a project screening assistant for public investment proposals.

Task:
Review the project form text and determine whether the project should be Low, Medium, or High Priority.

Important instructions:
- Apply the prioritization criteria exactly as described below.
- Decide whether the project belongs to the Sectoral Projects list or Regional Projects list based on cost.
- For projects below PHP 200 million, use the Sector Prioritization Criteria and RDP sectoral outcome criteria.
- For projects PHP 200 million and above, use the Regional Prioritization Criteria.
- Treat the negative list as score deductions, not automatic disqualification, and explain each match.
- Read the "Physical Accomplishment" and "Financial Accomplishment" fields carefully.
- Physical Accomplishment means completed work or outputs already delivered.
- Financial Accomplishment means how much budget has already been spent.
- If spending is high but physical accomplishment is low, flag this as a risk.
- Use the weighted criteria to calculate priority_score on a 0 to 100 scale.
- If data needed for a criterion is missing, score that criterion conservatively and mention the missing data in risk_flags or short_justification.

{SECTOR_PRIORITIZATION_CRITERIA}

{REGIONAL_PRIORITIZATION_CRITERIA}

Negative list for score deduction:
{chr(10).join(f"- {item}" for item in NEGATIVE_LIST_CRITERIA)}

Output rules:
- Respond only with valid JSON.
- Do not wrap the JSON in markdown.
- Include all fields requested in the schema.
""".strip()

    user_prompt = f"""
Analyze the following form text:

{form_text}

Return JSON with exactly these top-level keys:
- project_summary
- extracted_fields
- negative_matches
- risk_flags
- progress_assessment
- criterion_scores
- priority_score
- priority_grade
- short_justification

For extracted_fields, include any fields you can identify from the form such as:
agency_name, program, project_activity, location, description, objective,
funding_source, start_year, end_year, development_sector, main_chapter,
status, physical_accomplishment, financial_accomplishment, remarks.

For criterion_scores, return an object with exactly these keys:
- projects_programs_criterion
- rdp_outcomes
- regional_prioritization

For projects_programs_criterion, include:
- total_score
- max_score
- items
Each item must include: criterion, raw_score, weight, weighted_score, remarks.

For rdp_outcomes, include:
- sector_used
- total_score
- max_score
- items
Each item must include: sub_criterion, raw_score, weight, weighted_score, remarks.
The sector_used value must identify which RDP sectoral criteria group was used, such as Economic, Environment, Infrastructure, Financial and Development Administration, or Social.

For regional_prioritization, include:
- applicable
- reason
- total_score
- max_score
- items
Each item must include: criterion, raw_score, weight, weighted_score, remarks.
If the project is below PHP 200 million, set applicable to false, explain that it is a Sectoral Project, and return an empty items list.

For priority_grade, use one of:
- Low Priority
- Medium Priority
- High Priority

For priority_score, use an integer from 0 to 100.
""".strip()

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def analyze_with_groq(form_text: str, model: str = "llama-3.3-70b-versatile") -> Dict[str, Any]:
    api_key = get_groq_api_key()
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured.")

    try:
        groq_module = importlib.import_module("groq")
    except ImportError as exc:
        raise RuntimeError("The groq package is not installed.") from exc

    Groq = getattr(groq_module, "Groq", None)
    if Groq is None:
        raise RuntimeError("The groq package is not installed.")

    client = Groq(api_key=api_key)

    messages = build_prompt(form_text)

    completion_args = {
        "model": model,
        "messages": messages,
        "response_format": {"type": "json_object"},
        "temperature": 0.1,
        "max_tokens": 2200,
    }
    response = client.chat.completions.create(**completion_args)

    content = response.choices[0].message.content or ""
    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Groq returned invalid JSON: {exc}\n\nRaw output:\n{content}") from exc

    return data


def coerce_string_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value.strip() else []
    if not isinstance(value, list):
        value = [value]

    items = []
    for item in value:
        if item is None:
            continue
        if isinstance(item, dict):
            text = (
                item.get("keyword")
                or item.get("match")
                or item.get("title")
                or item.get("description")
                or json.dumps(item, ensure_ascii=False)
            )
        else:
            text = str(item)
        text = text.strip()
        if text:
            items.append(text)
    return items


def coerce_number(value: Any, default: float = 0) -> float:
    if isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        match = re.search(r"-?\d+(?:\.\d+)?", value.replace(",", ""))
        if match:
            try:
                return float(match.group(0))
            except ValueError:
                return default
    return default


def normalize_score_item(item: Any, criterion_key: str = "criterion") -> Dict[str, Any]:
    if not isinstance(item, dict):
        item = {criterion_key: str(item)}
    label = item.get(criterion_key) or item.get("criterion") or item.get("sub_criterion") or item.get("name") or ""
    return {
        criterion_key: str(label or "").strip(),
        "raw_score": coerce_number(item.get("raw_score")),
        "weight": coerce_number(item.get("weight")),
        "weighted_score": coerce_number(item.get("weighted_score")),
        "remarks": str(item.get("remarks") or item.get("justification") or "").strip(),
    }


def normalize_criterion_scores(value: Any) -> Dict[str, Any]:
    if not isinstance(value, dict):
        value = {}

    pap = value.get("projects_programs_criterion")
    if not isinstance(pap, dict):
        pap = {}
    pap_items = pap.get("items") if isinstance(pap.get("items"), list) else []

    rdp = value.get("rdp_outcomes")
    if not isinstance(rdp, dict):
        rdp = {}
    rdp_items = rdp.get("items") if isinstance(rdp.get("items"), list) else []

    regional = value.get("regional_prioritization")
    if not isinstance(regional, dict):
        regional = {}
    regional_items = regional.get("items") if isinstance(regional.get("items"), list) else []

    return {
        "projects_programs_criterion": {
            "total_score": coerce_number(pap.get("total_score")),
            "max_score": coerce_number(pap.get("max_score"), 50),
            "items": [normalize_score_item(item, "criterion") for item in pap_items],
        },
        "rdp_outcomes": {
            "sector_used": str(rdp.get("sector_used") or "").strip(),
            "total_score": coerce_number(rdp.get("total_score")),
            "max_score": coerce_number(rdp.get("max_score"), 50),
            "items": [normalize_score_item(item, "sub_criterion") for item in rdp_items],
        },
        "regional_prioritization": {
            "applicable": bool(regional.get("applicable")),
            "reason": str(regional.get("reason") or "").strip(),
            "total_score": coerce_number(regional.get("total_score")),
            "max_score": coerce_number(regional.get("max_score"), 100),
            "items": [normalize_score_item(item, "criterion") for item in regional_items],
        },
    }


def normalize_ai_result(result: Dict[str, Any]) -> Dict[str, Any]:
    extracted_fields = result.get("extracted_fields")
    if not isinstance(extracted_fields, dict):
        extracted_fields = {}

    score = result.get("priority_score")
    if isinstance(score, bool):
        score = None
    elif isinstance(score, (int, float)):
        score = int(score)
    elif isinstance(score, str):
        match = re.search(r"\d{1,3}", score)
        score = int(match.group(0)) if match else None
    else:
        score = None

    grade = str(result.get("priority_grade") or "").strip()
    if grade:
        grade_lookup = {
            "low": "Low Priority",
            "low priority": "Low Priority",
            "medium": "Medium Priority",
            "medium priority": "Medium Priority",
            "high": "High Priority",
            "high priority": "High Priority",
        }
        grade = grade_lookup.get(grade.lower(), grade)

    return {
        **result,
        "project_summary": str(result.get("project_summary") or ""),
        "extracted_fields": extracted_fields,
        "negative_matches": coerce_string_list(result.get("negative_matches")),
        "risk_flags": coerce_string_list(result.get("risk_flags")),
        "progress_assessment": str(result.get("progress_assessment") or ""),
        "criterion_scores": normalize_criterion_scores(result.get("criterion_scores")),
        "priority_score": score,
        "priority_grade": grade,
        "short_justification": str(result.get("short_justification") or ""),
    }


def apply_local_scoring_fallback(result: Dict[str, Any], form_text: str) -> Dict[str, Any]:
    """
    If the model omitted score/grade or returned something inconsistent,
    this function normalizes it.
    """
    text = form_text.lower()
    result = normalize_ai_result(result)
    score = result.get("priority_score")

    # Start from model score if valid
    if not isinstance(score, int):
        score = 50

    # Simple keyword nudges as a safety net
    for phrase in NEGATIVE_LIST_CRITERIA:
        if phrase.lower() in text:
            score -= 15

    for phrase, bonus in {
        "health": 8,
        "education": 8,
        "water": 8,
        "sanitation": 8,
        "transport": 8,
        "flood control": 10,
        "disaster": 10,
        "climate": 8,
        "public safety": 8,
        "digital service": 6,
        "transparency": 6,
        "accountability": 6,
        "livelihood": 8,
    }.items():
        if phrase in text:
            score += bonus

    # Extra penalty if financial accomplishment is very high and physical accomplishment is weak
    physical = str(result.get("extracted_fields", {}).get("physical_accomplishment", "")).lower()
    financial = str(result.get("extracted_fields", {}).get("financial_accomplishment", "")).lower()

    # Very simple heuristic: detect percentages like "80%" or "75 percent"
    def extract_pct(s: str) -> Optional[int]:
        m = re.search(r"(\d{1,3})\s*%", s)
        if m:
            return int(m.group(1))
        m = re.search(r"(\d{1,3})\s*(?:percent|pct)\b", s)
        if m:
            return int(m.group(1))
        return None

    p = extract_pct(physical)
    f = extract_pct(financial)
    if p is not None and f is not None and f - p >= 40:
        score -= 10
        result.setdefault("risk_flags", [])
        if "high spending but low completion" not in [x.lower() for x in result["risk_flags"]]:
            result["risk_flags"].append("High spending but low completion")

    score = max(0, min(100, score))

    if score >= 70:
        normalized_grade = "High Priority"
    elif score >= 40:
        normalized_grade = "Medium Priority"
    else:
        normalized_grade = "Low Priority"

    result["priority_score"] = score
    result["priority_grade"] = normalized_grade
    return result


def score_project(title, description="", profile_data: Optional[Dict[str, Any]] = None):
    form_text = build_form_text(title, description, profile_data)
    
    try:
        result = analyze_with_groq(form_text)
        result = apply_local_scoring_fallback(result, form_text)
        
        return {
            "score": result.get("priority_score", 50),
            "grade": result.get("priority_grade", "Medium Priority"),
            "summary": result.get("project_summary", ""),
            "justification": result.get("short_justification", ""),
            "negative_matches": result.get("negative_matches", []),
            "risk_flags": result.get("risk_flags", []),
            "extracted_fields": result.get("extracted_fields", {}),
            "progress_assessment": result.get("progress_assessment", ""),
            "criterion_scores": result.get("criterion_scores", normalize_criterion_scores({})),
        }
    except Exception as e:
        # Fallback to simple keyword scoring if AI fails
        text = normalize(f"{title} {description}")
        score = 50  # base score

        negative_hits = []
        positive_hits = []

        for keyword, penalty in NEGATIVE_KEYWORDS.items():
            if keyword in text:
                score -= penalty
                negative_hits.append(keyword)

        for keyword, bonus in POSITIVE_KEYWORDS.items():
            if keyword in text:
                score += bonus
                positive_hits.append(keyword)

        score = max(0, min(100, score))

        if score >= 70:
            grade = "High Priority"
        elif score >= 40:
            grade = "Medium Priority"
        else:
            grade = "Low Priority"

        return {
            "score": score,
            "grade": grade,
            "summary": "",
            "justification": f"Fallback keyword-based scoring due to AI error: {e}",
            "negative_matches": negative_hits,
            "risk_flags": [],
            "extracted_fields": {},
            "progress_assessment": "",
            "criterion_scores": normalize_criterion_scores({}),
        }
