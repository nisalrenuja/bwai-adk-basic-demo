from __future__ import annotations

from typing import Literal

import dotenv
from google.adk.agents import Agent

dotenv.load_dotenv()

# ── Data ─────────────────────────────────────────────────────────────────────

COURSES = [
    {"code": "CS2101", "name": "Data Structures and Algorithms",  "department": "IT",          "semester": 2, "credits": 3, "lecturer": "Dr. Perera"},
    {"code": "CS2102", "name": "Database Management Systems",     "department": "IT",          "semester": 2, "credits": 3, "lecturer": "Ms. Jayawardena"},
    {"code": "CS2103", "name": "Software Engineering",            "department": "IT",          "semester": 2, "credits": 3, "lecturer": "Dr. Fernando"},
    {"code": "CS2104", "name": "Computer Networks",               "department": "IT",          "semester": 2, "credits": 3, "lecturer": "Mr. Dissanayake"},
    {"code": "BM2101", "name": "Marketing Management",            "department": "Business",    "semester": 2, "credits": 3, "lecturer": "Ms. Silva"},
    {"code": "BM2102", "name": "Financial Accounting",            "department": "Business",    "semester": 2, "credits": 3, "lecturer": "Dr. Wijesinghe"},
    {"code": "EN2101", "name": "Structural Analysis",             "department": "Engineering", "semester": 2, "credits": 4, "lecturer": "Prof. Rathnayake"},
    {"code": "EN2102", "name": "Thermodynamics",                  "department": "Engineering", "semester": 2, "credits": 3, "lecturer": "Dr. Bandara"},
]

EXAM_SCHEDULE = [
    {"course_code": "CS2101", "course_name": "Data Structures and Algorithms", "department": "IT",          "semester": 2, "date": "2025-08-14", "time": "09:00 AM", "venue": "Examination Hall A", "duration_hours": 3},
    {"course_code": "CS2102", "course_name": "Database Management Systems",    "department": "IT",          "semester": 2, "date": "2025-08-16", "time": "09:00 AM", "venue": "Examination Hall A", "duration_hours": 3},
    {"course_code": "CS2103", "course_name": "Software Engineering",           "department": "IT",          "semester": 2, "date": "2025-08-18", "time": "01:00 PM", "venue": "Examination Hall B", "duration_hours": 3},
    {"course_code": "CS2104", "course_name": "Computer Networks",              "department": "IT",          "semester": 2, "date": "2025-08-20", "time": "09:00 AM", "venue": "Examination Hall A", "duration_hours": 2},
    {"course_code": "BM2101", "course_name": "Marketing Management",           "department": "Business",    "semester": 2, "date": "2025-08-15", "time": "09:00 AM", "venue": "Examination Hall C", "duration_hours": 3},
    {"course_code": "BM2102", "course_name": "Financial Accounting",           "department": "Business",    "semester": 2, "date": "2025-08-19", "time": "01:00 PM", "venue": "Examination Hall C", "duration_hours": 3},
    {"course_code": "EN2101", "course_name": "Structural Analysis",            "department": "Engineering", "semester": 2, "date": "2025-08-13", "time": "09:00 AM", "venue": "Examination Hall D", "duration_hours": 3},
    {"course_code": "EN2102", "course_name": "Thermodynamics",                 "department": "Engineering", "semester": 2, "date": "2025-08-17", "time": "09:00 AM", "venue": "Examination Hall D", "duration_hours": 3},
]

REGISTRATION_INFO = {
    "current_semester": 2,
    "academic_year": "2024/2025",
    "registration_deadline": "2025-07-31",
    "late_registration_deadline": "2025-08-07",
    "late_fee": "Rs. 1,500",
    "steps": [
        "Log in to the Student Portal at portal.university.lk",
        "Navigate to Registration > Course Selection",
        "Select your courses for the semester",
        "Confirm your selection and download the registration slip",
        "Pay the semester fees at the Finance Division or via online banking",
        "Upload proof of payment on the Student Portal within 3 working days",
    ],
    "finance_division_hours": "Monday to Friday, 8:30 AM to 3:30 PM",
    "contact": "registrar@university.lk | +94 11 234 5678",
}

CAMPUS_INFO = {
    "library": {
        "name": "Main University Library",
        "weekday_hours": "7:30 AM to 9:00 PM (Monday to Friday)",
        "weekend_hours": "8:00 AM to 5:00 PM (Saturday and Sunday)",
        "note": "Library closes at 5:00 PM on public holidays.",
        "contact": "library@university.lk | +94 11 234 5690",
    },
    "canteen": {
        "main_canteen": "Open 7:00 AM to 7:00 PM, Monday to Saturday",
        "engineering_canteen": "Open 7:30 AM to 5:00 PM, Monday to Friday",
        "note": "The main canteen is closed on Sundays and public holidays.",
    },
    "hostel": {
        "male_hostel": "Block A and Block B — Warden: Mr. Kumara, +94 77 123 4567",
        "female_hostel": "Block C — Warden: Ms. Dilrukshi, +94 77 234 5678",
        "visitor_hours": "4:00 PM to 7:00 PM on weekdays, 9:00 AM to 7:00 PM on weekends",
        "contact": "hostel@university.lk",
    },
    "clinic": {
        "hours": "Monday to Friday, 8:00 AM to 4:00 PM",
        "emergency": "After hours, contact the security post for emergency assistance.",
        "contact": "clinic@university.lk | +94 11 234 5695",
        "note": "Free consultation for registered students. Bring your student ID.",
    },
    "sports": {
        "grounds": "Open 5:30 AM to 8:00 PM daily",
        "gym": "Open 5:30 AM to 9:00 PM, Monday to Saturday",
        "bookings": "Sports equipment and court bookings via the Student Portal",
        "contact": "sports@university.lk",
    },
    "general": {
        "main_office": "Monday to Friday, 8:30 AM to 4:30 PM",
        "security": "24 hours, 7 days a week — +94 11 234 5600",
        "student_affairs": "Monday to Friday, 8:30 AM to 4:00 PM",
        "wifi": "Eduroam and UniWifi available across campus. Register via the Student Portal.",
    },
}

# ── Tools ─────────────────────────────────────────────────────────────────────


def list_courses(
    department: Literal["IT", "Business", "Engineering", "Science"] | None = None,
    semester: int | None = None,
) -> dict:
    """List available courses, optionally filtered by department or semester.

    Args:
        department: Filter by department name.
        semester: Filter by semester number (1 or 2).

    Returns:
        Matching courses and a count.
    """
    results = []
    for course in COURSES:
        if department and course["department"] != department:
            continue
        if semester and course["semester"] != semester:
            continue
        results.append(course)
    return {"status": "success", "count": len(results), "courses": results}


def get_exam_schedule(
    department: Literal["IT", "Business", "Engineering", "Science"],
    semester: int,
) -> dict:
    """Get the final examination schedule for a department and semester.

    Args:
        department: The academic department.
        semester: Semester number.

    Returns:
        All exam dates, times, and venues for that department and semester.
    """
    results = [
        e for e in EXAM_SCHEDULE
        if e["department"] == department and e["semester"] == semester
    ]
    if not results:
        return {
            "status": "error",
            "message": f"No exam schedule found for {department}, Semester {semester}.",
        }
    return {"status": "success", "count": len(results), "exams": results}


def get_registration_info() -> dict:
    """Get course registration steps, deadlines, fees, and contact details.

    Returns:
        Registration procedure, deadline dates, and fee information.
    """
    return {"status": "success", "registration": REGISTRATION_INFO}


def get_campus_info(
    topic: Literal["library", "canteen", "hostel", "clinic", "sports", "general"],
) -> dict:
    """Get campus facility information and frequently asked questions.

    Args:
        topic: The campus facility or topic to look up.

    Returns:
        Hours, contacts, and relevant information for that facility.
    """
    info = CAMPUS_INFO.get(topic)
    if not info:
        return {"status": "error", "message": f"No information found for topic: {topic}"}
    return {"status": "success", "topic": topic, "info": info}


# ── Agent ─────────────────────────────────────────────────────────────────────

root_agent = Agent(
    name="university_helpdesk",
    model="gemini-3.1-flash-lite",
    description="A helpful university helpdesk assistant for students.",
    instruction="""
You are the official virtual helpdesk assistant for the university.
You help students with course information, examination schedules,
registration procedures, and campus facility information.

Always be polite, clear, and accurate. Never guess or make up information.
Every answer must be grounded in what the tools return.

When a student asks about courses, use list_courses.
When a student asks about exams or exam schedules, use get_exam_schedule.
When a student asks about registration, deadlines, or fees, use get_registration_info.
When a student asks about campus facilities — library, canteen, hostel, clinic,
sports — use get_campus_info.

If a student's question is unclear, ask one simple clarifying question before
calling a tool. For example, if they ask about exams but do not mention their
department, ask which department they are in.

Respond in a friendly, professional tone. Keep answers concise and actionable.
""",
    tools=[
        list_courses,
        get_exam_schedule,
        get_registration_info,
        get_campus_info,
    ],
)
