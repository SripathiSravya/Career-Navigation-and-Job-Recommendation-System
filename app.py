from flask import Flask, render_template, request
from PyPDF2 import PdfReader
from werkzeug.exceptions import RequestEntityTooLarge
import re
from pathlib import Path

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

ALLOWED_RESUME_EXTENSIONS = {".pdf"}


# ============================================================
# 1. SKILL ALIASES
# ============================================================

SKILL_ALIASES = {
    "python": ["python", "python programming"],
    "java": ["java", "java programming"],
    "c": ["c programming", "c language"],
    "c++": ["c++", "cpp"],
    "javascript": ["javascript", "js"],
    "html": ["html", "html5"],
    "css": ["css", "css3"],
    "react": ["react", "react.js", "reactjs"],
    "node.js": ["node.js", "nodejs", "node js"],
    "sql": ["sql", "structured query language"],
    "mysql": ["mysql"],
    "postgresql": ["postgresql", "postgres"],
    "oracle": ["oracle database"],
    "mongodb": ["mongodb", "mongo db"],
    "database": ["database", "databases", "dbms"],
    "git": ["git", "github", "gitlab"],
    "oops": ["oops", "oop", "object oriented programming"],
    "data structures": ["data structures", "data structure"],
    "algorithms": ["algorithms", "algorithm"],
    "api": ["api", "apis", "rest api", "restful api"],
    "django": ["django"],
    "flask": ["flask"],
    "spring": ["spring boot", "spring framework"],
    "android": ["android development", "android"],
    "kotlin": ["kotlin"],
    "flutter": ["flutter"],
    "react native": ["react native"],
    "excel": ["excel", "microsoft excel", "pivot tables", "pivottables"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "statistics": ["statistics", "statistical analysis"],
    "data analysis": ["data analysis", "data analytics", "data analyst"],
    "data science": ["data science", "data scientist"],
    "data visualization": ["data visualization", "data visualisation"],
    "power bi": ["power bi", "powerbi"],
    "tableau": ["tableau"],
    "machine learning": ["machine learning", "ml"],
    "artificial intelligence": ["artificial intelligence", "ai"],
    "deep learning": ["deep learning"],
    "tensorflow": ["tensorflow"],
    "pytorch": ["pytorch"],
    "scikit-learn": ["scikit-learn", "scikit learn", "sklearn"],
    "cloud computing": ["cloud computing"],
    "aws": ["aws", "amazon web services"],
    "azure": ["azure", "microsoft azure"],
    "linux": ["linux"],
    "computer networks": [
        "computer networks", "networking", "computer networking"
    ],
    "cybersecurity": [
        "cybersecurity", "cyber security", "information security"
    ],
    "network security": ["network security"],
    "ethical hacking": ["ethical hacking"],
    "penetration testing": ["penetration testing", "pentesting"],
    "docker": ["docker"],
    "kubernetes": ["kubernetes", "k8s"],
    "jenkins": ["jenkins"],
    "ci/cd": ["ci/cd", "continuous integration", "continuous delivery"],
    "testing": ["software testing", "testing", "test cases"],
    "manual testing": ["manual testing"],
    "selenium": ["selenium"],
    "automation testing": ["automation testing", "test automation"],
    "debugging": ["debugging", "debug"],
    "operating systems": ["operating systems", "operating system"],
    "software engineering": ["software engineering"],
    "ui/ux": ["ui/ux", "ui ux", "user interface", "user experience"],
    "figma": ["figma"],
    "adobe xd": ["adobe xd"],
    "photoshop": ["photoshop", "adobe photoshop"],
    "communication": ["communication", "communication skills"],
    "teamwork": ["teamwork", "team work", "collaboration"],
    "leadership": ["leadership", "leadership skills"],
    "time management": ["time management"],
    "project management": ["project management"],
    "presentation": ["presentation skills", "presentations"],
    "problem solving": ["problem solving", "problem-solving"],
    "business analysis": ["business analysis", "business analyst"],
}


# ============================================================
# 2. CAREER DATABASE: 25 CAREERS
# ============================================================

CAREERS = {
    "Python Developer": ["python", "sql", "git", "oops", "api"],
    "Java Developer": ["java", "sql", "oops", "git", "api"],
    "Software Developer": [
        "python", "java", "sql", "git", "oops", "data structures"
    ],
    "Full Stack Developer": [
        "html", "css", "javascript", "react", "node.js", "sql"
    ],
    "Backend Developer": ["python", "flask", "sql", "git", "api"],
    "Frontend Developer": ["html", "css", "javascript", "react"],
    "Web Developer": ["html", "css", "javascript", "git"],
    "Mobile App Developer": ["java", "kotlin", "android"],
    "Data Analyst": ["python", "sql", "pandas", "numpy", "excel"],
    "Data Scientist": [
        "python", "sql", "pandas", "numpy",
        "data science", "machine learning"
    ],
    "Machine Learning Engineer": [
        "python", "machine learning", "pandas", "numpy", "sql"
    ],
    "AI Engineer": [
        "python", "artificial intelligence",
        "machine learning", "deep learning"
    ],
    "BI Analyst": [
        "sql", "excel", "power bi", "tableau", "data analysis"
    ],
    "Cloud Engineer": [
        "aws", "azure", "linux", "computer networks", "docker"
    ],
    "DevOps Engineer": [
        "linux", "docker", "kubernetes", "jenkins", "git"
    ],
    "Cloud Developer": ["python", "aws", "azure", "docker", "git"],
    "Cybersecurity Analyst": [
        "cybersecurity", "computer networks", "linux", "python"
    ],
    "Security Engineer": [
        "cybersecurity", "network security", "linux",
        "computer networks", "penetration testing"
    ],
    "Network Engineer": [
        "computer networks", "linux", "network security"
    ],
    "Database Administrator": ["sql", "mysql", "mongodb", "linux"],
    "Database Developer": ["sql", "mysql", "mongodb", "python"],
    "Systems Analyst": [
        "sql", "python", "business analysis", "problem solving"
    ],
    "QA/Test Engineer": ["testing", "java", "sql", "git"],
    "Automation Test Engineer": [
        "testing", "selenium", "java", "python"
    ],
    "UI/UX Designer": ["figma", "ui/ux", "communication"],
}


# ============================================================
# 3. ILLUSTRATIVE CAREER TREND DATA
# Sample project data, not live market information.
# ============================================================

CAREER_TRENDS = {
    "Python Developer": {
        "demand": "High",
        "growth": "Positive",
        "future": "Python is used in automation, web development and data applications."
    },
    "Java Developer": {
        "demand": "High",
        "growth": "Positive",
        "future": "Java remains useful for enterprise and backend applications."
    },
    "Software Developer": {
        "demand": "High",
        "growth": "Positive",
        "future": "Software development supports applications across many industries."
    },
    "Full Stack Developer": {
        "demand": "High",
        "growth": "Positive",
        "future": "Full-stack skills cover both user interfaces and server-side applications."
    },
    "Backend Developer": {
        "demand": "High",
        "growth": "Positive",
        "future": "Backend development supports APIs, business logic and data processing."
    },
    "Frontend Developer": {
        "demand": "High",
        "growth": "Positive",
        "future": "Frontend skills are useful for building accessible interactive websites."
    },
    "Web Developer": {
        "demand": "High",
        "growth": "Positive",
        "future": "Web development supports websites and browser-based applications."
    },
    "Mobile App Developer": {
        "demand": "High",
        "growth": "Positive",
        "future": "Mobile development supports applications for phones and tablets."
    },
    "Data Analyst": {
        "demand": "High",
        "growth": "Positive",
        "future": "Organizations use data analysis to support decisions."
    },
    "Data Scientist": {
        "demand": "High",
        "growth": "Positive",
        "future": "Data science combines statistics, programming and analytical methods."
    },
    "Machine Learning Engineer": {
        "demand": "High",
        "growth": "Positive",
        "future": "Machine learning engineering develops and maintains predictive systems."
    },
    "AI Engineer": {
        "demand": "High",
        "growth": "Positive",
        "future": "AI engineering applies artificial intelligence to practical problems."
    },
    "BI Analyst": {
        "demand": "High",
        "growth": "Positive",
        "future": "Business intelligence turns business data into reports and dashboards."
    },
    "Cloud Engineer": {
        "demand": "High",
        "growth": "Positive",
        "future": "Cloud engineering supports infrastructure, storage and deployment."
    },
    "DevOps Engineer": {
        "demand": "High",
        "growth": "Positive",
        "future": "DevOps practices help teams automate software delivery and operations."
    },
    "Cloud Developer": {
        "demand": "High",
        "growth": "Positive",
        "future": "Cloud developers build applications that use cloud services."
    },
    "Cybersecurity Analyst": {
        "demand": "High",
        "growth": "Positive",
        "future": "Security analysts help monitor systems and investigate security events."
    },
    "Security Engineer": {
        "demand": "High",
        "growth": "Positive",
        "future": "Security engineers design and improve technical security controls."
    },
    "Network Engineer": {
        "demand": "Moderate",
        "growth": "Positive",
        "future": "Network engineers configure, maintain and troubleshoot networks."
    },
    "Database Administrator": {
        "demand": "Moderate",
        "growth": "Positive",
        "future": "Database administrators maintain database availability and performance."
    },
    "Database Developer": {
        "demand": "Moderate",
        "growth": "Positive",
        "future": "Database developers design data structures and database solutions."
    },
    "Systems Analyst": {
        "demand": "Moderate",
        "growth": "Positive",
        "future": "Systems analysts connect business needs with technical solutions."
    },
    "QA/Test Engineer": {
        "demand": "High",
        "growth": "Positive",
        "future": "Software testing helps identify defects and improve product quality."
    },
    "Automation Test Engineer": {
        "demand": "High",
        "growth": "Positive",
        "future": "Test automation helps teams repeat checks more efficiently."
    },
    "UI/UX Designer": {
        "demand": "Moderate",
        "growth": "Positive",
        "future": "UI/UX design focuses on usable and understandable digital experiences."
    },
}


# ============================================================
# 4. EXAMPLE JOB TITLES
# These are role examples, not current vacancies.
# ============================================================

JOB_DATABASE = {
    "Python Developer": [
        "Python Developer",
        "Backend Python Developer",
        "Python Software Developer"
    ],
    "Java Developer": [
        "Java Developer",
        "Java Backend Developer",
        "Java Software Engineer"
    ],
    "Software Developer": [
        "Software Developer",
        "Application Developer",
        "Software Engineer"
    ],
    "Full Stack Developer": [
        "Full Stack Developer",
        "Web Application Developer",
        "Full Stack Software Engineer"
    ],
    "Backend Developer": [
        "Backend Developer",
        "API Developer",
        "Backend Software Engineer"
    ],
    "Frontend Developer": [
        "Frontend Developer",
        "React Developer",
        "UI Developer"
    ],
    "Web Developer": [
        "Web Developer",
        "Website Developer",
        "Web Application Developer"
    ],
    "Mobile App Developer": [
        "Android Developer",
        "Mobile Application Developer",
        "Mobile App Developer"
    ],
    "Data Analyst": [
        "Data Analyst",
        "Junior Data Analyst",
        "Business Data Analyst"
    ],
    "Data Scientist": [
        "Data Scientist",
        "Junior Data Scientist",
        "Data Science Associate"
    ],
    "Machine Learning Engineer": [
        "Machine Learning Engineer",
        "ML Engineer",
        "Junior ML Engineer"
    ],
    "AI Engineer": [
        "AI Engineer",
        "Artificial Intelligence Engineer",
        "Junior AI Engineer"
    ],
    "BI Analyst": [
        "Business Intelligence Analyst",
        "BI Analyst",
        "Business Data Analyst"
    ],
    "Cloud Engineer": [
        "Cloud Engineer",
        "Cloud Infrastructure Engineer",
        "Junior Cloud Engineer"
    ],
    "DevOps Engineer": [
        "DevOps Engineer",
        "Junior DevOps Engineer",
        "DevOps Associate"
    ],
    "Cloud Developer": [
        "Cloud Developer",
        "Cloud Application Developer",
        "Cloud Software Engineer"
    ],
    "Cybersecurity Analyst": [
        "Cybersecurity Analyst",
        "Security Analyst",
        "SOC Analyst"
    ],
    "Security Engineer": [
        "Security Engineer",
        "Information Security Engineer",
        "Cybersecurity Engineer"
    ],
    "Network Engineer": [
        "Network Engineer",
        "Network Administrator",
        "Junior Network Engineer"
    ],
    "Database Administrator": [
        "Database Administrator",
        "Database Support Engineer",
        "Junior DBA"
    ],
    "Database Developer": [
        "Database Developer",
        "SQL Developer",
        "Database Application Developer"
    ],
    "Systems Analyst": [
        "Systems Analyst",
        "Business Systems Analyst",
        "IT Systems Analyst"
    ],
    "QA/Test Engineer": [
        "QA Engineer",
        "Software Test Engineer",
        "Quality Analyst"
    ],
    "Automation Test Engineer": [
        "Automation Test Engineer",
        "Selenium Automation Engineer",
        "QA Automation Engineer"
    ],
    "UI/UX Designer": [
        "UI/UX Designer",
        "UX Designer",
        "UI Designer"
    ],
}
# ============================================================
# 5. SKILL MATCHING HELPERS
# ============================================================

def _contains_skill(text, skill):
    """
    Check whether a skill appears as a complete word or phrase.
    """
    if not text or not skill:
        return False

    pattern = r"(?<!\w)" + re.escape(skill.lower()) + r"(?!\w)"
    return re.search(pattern, text.lower()) is not None


def normalize_technical_skills(skills):
    """
    Convert user-provided skill names into standardized skill names.
    """
    normalized = []

    if isinstance(skills, str):
        skills = re.split(r"[,;\n|]+", skills)

    if not skills:
        return normalized

    for item in skills:
        if not isinstance(item, str):
            continue

        item = item.strip().lower()

        if not item:
            continue

        matched_skill = None

        # Match known aliases.
        for canonical, aliases in SKILL_ALIASES.items():
            if item == canonical.lower() or item in [
                alias.lower() for alias in aliases
            ]:
                matched_skill = canonical
                break

        # Preserve unknown skills instead of discarding them.
        if matched_skill is None:
            matched_skill = item

        if matched_skill not in normalized:
            normalized.append(matched_skill)

    return normalized


# ============================================================
# 6. EXTRACT SKILLS FROM RESUME TEXT
# ============================================================

def extract_technical_skills(text):
    """
    Extract skills only from a resume's skills section.

    This prevents words mentioned in project descriptions,
    career objectives, or other sections from being counted
    automatically as technical skills.
    """
    if not text:
        return []

    # Normalize line breaks and remove excess whitespace.
    text = text.replace("\r", "\n")
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    # Possible headings that begin the skills section.
    skill_headings = [
        "skills",
        "technical skills",
        "key skills",
        "professional skills",
        "core skills",
        "technical expertise",
        "areas of expertise",
        "technologies",
        "technical proficiencies",
    ]

    # Headings that signal the end of the skills section.
    stop_headings = [
        "education",
        "academic qualifications",
        "academic details",
        "work experience",
        "professional experience",
        "experience",
        "internship",
        "internships",
        "projects",
        "personal projects",
        "certifications",
        "certificates",
        "achievements",
        "awards",
        "languages",
        "interests",
        "hobbies",
        "career objective",
        "objective",
        "profile summary",
        "professional summary",
        "summary",
        "declaration",
        "contact",
        "personal details",
    ]

    skills_lines = []
    inside_skills_section = False

    for line in lines:
        # Clean common bullets and numbering.
        cleaned = re.sub(r"^[\s•●▪◦*+\-]+", "", line).strip()
        cleaned = re.sub(r"^\d+[\).]\s*", "", cleaned).strip()

        if not cleaned:
            continue

        heading = cleaned.lower().strip(" :.-")

        # Start collecting after a recognized skills heading.
        if heading in skill_headings:
            inside_skills_section = True
            continue

        # Stop at the next recognized resume section.
        if heading in stop_headings:
            if inside_skills_section:
                break
            continue

        # Also recognize headings such as "Education:".
        first_part = heading.split(":", 1)[0].strip()

        if first_part in stop_headings:
            if inside_skills_section:
                break
            continue

        if inside_skills_section:
            skills_lines.append(cleaned)

    # Do not scan the entire resume as a fallback.
    # If no skills section exists, return an empty list.
    if not skills_lines:
        return []

    extracted = []

    # Common labels used to categorize skills in resumes.
    category_labels = [
        "programming",
        "programming languages",
        "web technologies",
        "web development",
        "database",
        "databases",
        "tools",
        "frameworks",
        "libraries",
        "operating systems",
        "cloud technologies",
        "technical skills",
        "soft skills",
    ]

    for line in skills_lines:
        # Remove category labels such as:
        # "Programming: Python, Java"
        # "Database: MySQL, SQL"
        line = re.sub(
            r"^[A-Za-z /&+.-]{2,35}\s*:\s*",
            "",
            line
        ).strip()

        # Remove category labels without colons, when present.
        for label in category_labels:
            pattern = (
                r"^" + re.escape(label) + r"\s*[-–]\s*"
            )
            line = re.sub(pattern, "", line, flags=re.IGNORECASE)

        # Split lists into individual candidate items.
        candidates = re.split(r"[,;|•●]+", line)

        for candidate in candidates:
            candidate = candidate.strip().lower()

            if not candidate:
                continue

            # Remove common list formatting.
            candidate = re.sub(r"^[\s:.\-]+", "", candidate)
            candidate = re.sub(r"[\s:.\-]+$", "", candidate)

            # Ignore standalone category names.
            if candidate in category_labels:
                continue

            # Match only skills found in the skills section.
            for canonical, aliases in SKILL_ALIASES.items():
                possible_names = [canonical.lower()] + [
                    alias.lower() for alias in aliases
                ]

                for alias in possible_names:
                    if candidate == alias:
                        if canonical not in extracted:
                            extracted.append(canonical)
                        break
                else:
                    continue

                break

    return extracted


# ============================================================
# 7. EXTRACT SOFT SKILLS
# ============================================================

def extract_soft_skills(text):
    """
    Find common soft skills in the supplied text.
    """
    if not text:
        return []

    soft_skill_aliases = {
        "communication": [
            "communication",
            "communication skills",
            "verbal communication",
            "written communication",
        ],
        "teamwork": [
            "teamwork",
            "team work",
            "collaboration",
            "team player",
        ],
        "leadership": [
            "leadership",
            "leadership skills",
            "team leadership",
        ],
        "problem solving": [
            "problem solving",
            "problem-solving",
            "analytical thinking",
        ],
        "time management": [
            "time management",
            "time-management",
        ],
        "adaptability": [
            "adaptability",
            "adaptable",
            "flexibility",
        ],
        "creativity": [
            "creativity",
            "creative thinking",
        ],
        "critical thinking": [
            "critical thinking",
            "critical analysis",
        ],
        "presentation": [
            "presentation skills",
            "presentations",
        ],
        "project management": [
            "project management",
        ],
    }

    found = []

    text_lower = text.lower()

    for canonical, aliases in soft_skill_aliases.items():
        for alias in aliases:
            if _contains_skill(text_lower, alias):
                if canonical not in found:
                    found.append(canonical)
                break

    return found


# ============================================================
# 8. COMBINE TECHNICAL SKILLS
# ============================================================

def combine_technical_skills(profile_skills, resume_skills):
    """
    Combine skills entered in the form with skills extracted
    from the resume, removing duplicates.
    """
    combined = []

    profile_normalized = normalize_technical_skills(profile_skills)
    resume_normalized = normalize_technical_skills(resume_skills)

    for skill in profile_normalized + resume_normalized:
        if skill not in combined:
            combined.append(skill)

    return combined


# ============================================================
# 9. COMPARE SKILLS
# ============================================================

def compare_skills(user_skills, required_skills):
    """
    Compare a user's skills with a required skill list.
    """
    user_normalized = normalize_technical_skills(user_skills)
    required_normalized = normalize_technical_skills(required_skills)

    matched = []
    missing = []

    for skill in required_normalized:
        if skill in user_normalized:
            matched.append(skill)
        else:
            missing.append(skill)

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "total_required_skills": len(required_normalized),
        "total_matched_skills": len(matched),
    }
# ============================================================
# 10. RECOMMEND CAREERS
# ============================================================

def recommend_careers(user_skills):
    """
    Recommend career roles based on the user's matched skills.
    """
    normalized_skills = normalize_technical_skills(user_skills)
    recommendations = []

    for career, required_skills in CAREERS.items():
        comparison = compare_skills(
            normalized_skills,
            required_skills
        )

        total_required = comparison["total_required_skills"]
        total_matched = comparison["total_matched_skills"]

        if total_required > 0:
            match_percentage = round(
                (total_matched / total_required) * 100
            )
        else:
            match_percentage = 0

        recommendations.append({
            "career": career,
            "role": career,
            "match_percentage": match_percentage,
            "matched_skills": comparison["matched_skills"],
            "missing_skills": comparison["missing_skills"],
            "total_required_skills": total_required,
            "total_matched_skills": total_matched,
        })

    # Highest matching careers appear first.
    recommendations.sort(
        key=lambda item: item["match_percentage"],
        reverse=True
    )

    return recommendations


# ============================================================
# 11. ANALYZE SKILL GAPS
# ============================================================

def analyze_skill_gap(user_skills, career):
    """
    Identify skills the user has and skills still required
    for the selected career.
    """
    required_skills = CAREERS.get(career, [])

    comparison = compare_skills(
        user_skills,
        required_skills
    )

    total_required = comparison["total_required_skills"]
    total_matched = comparison["total_matched_skills"]

    if total_required > 0:
        readiness_percentage = round(
            total_matched / total_required * 100
        )
    else:
        readiness_percentage = 0

    return {
        "career": career,
        "required_skills": required_skills,
        "matched_skills": comparison["matched_skills"],
        "missing_skills": comparison["missing_skills"],
        "total_required_skills": total_required,
        "total_matched_skills": total_matched,
        "readiness_percentage": readiness_percentage,
    }


# ============================================================
# 12. CAREER TREND ANALYSIS
# ============================================================

def get_career_trend(career):
    """
    Return the illustrative career trend information
    stored in CAREER_TRENDS.
    """
    trend = CAREER_TRENDS.get(career)

    if not trend:
        return {
            "career": career,
            "demand": "Information unavailable",
            "growth": "Information unavailable",
            "future": (
                "No trend information is available for this career."
            ),
        }

    return {
        "career": career,
        "demand": trend["demand"],
        "growth": trend["growth"],
        "future": trend["future"],
    }


# ============================================================
# 13. RECOMMENDED JOB TITLES
# ============================================================

def get_recommended_job_roles(career_recommendations):
    """
    Generate example job titles from the recommended careers.

    These are example job titles, not live job vacancies.
    """
    recommended_roles = []

    for recommendation in career_recommendations:
        career = recommendation.get(
            "career",
            recommendation.get("role", "")
        )

        match_percentage = recommendation.get(
            "match_percentage", 0
        )

        job_titles = JOB_DATABASE.get(career, [])

        for title in job_titles:
            recommended_roles.append({
                "career": career,
                "job_title": title,
                "match_percentage": match_percentage,
            })

    return recommended_roles
# ============================================================
# 14. RESUME QUALITY ANALYSIS
# ============================================================

def calculate_resume_quality(
    name,
    education,
    experience,
    skills,
    resume_text=""
):
    """
    Calculate an indicative resume quality score based on
    available profile information and resume content.
    """
    score = 0
    feedback = []

    if name and name.strip():
        score += 10
    else:
        feedback.append("Add your full name.")

    if education and education.strip():
        score += 15
    else:
        feedback.append("Add your educational qualifications.")

    if experience and experience.strip():
        score += 15
    else:
        feedback.append("Add your experience or internship details.")

    normalized_skills = normalize_technical_skills(skills)

    if len(normalized_skills) >= 5:
        score += 20
    elif len(normalized_skills) >= 3:
        score += 15
        feedback.append("Consider adding more relevant technical skills.")
    elif normalized_skills:
        score += 10
        feedback.append("Add more relevant technical skills.")
    else:
        feedback.append("Add relevant technical skills.")

    if resume_text and len(resume_text.strip()) >= 200:
        score += 15
    else:
        feedback.append(
            "Include more detailed information in your resume."
        )

    if resume_text and re.search(
        r"\b(project|projects|internship|internships)\b",
        resume_text,
        re.IGNORECASE
    ):
        score += 15
    else:
        feedback.append(
            "Include relevant projects or internship experience."
        )

    if resume_text and re.search(
        r"\b(email|phone|contact)\b",
        resume_text,
        re.IGNORECASE
    ):
        score += 10
    else:
        feedback.append(
            "Make sure your contact information is included."
        )

    score = min(score, 100)

    if score >= 80:
        quality_level = "Excellent"
    elif score >= 60:
        quality_level = "Good"
    elif score >= 40:
        quality_level = "Average"
    else:
        quality_level = "Needs Improvement"

    if not feedback:
        feedback.append(
            "Your resume contains several useful sections. "
            "Continue tailoring it to the role you want."
        )

    return {
        "score": score,
        "quality_score": score,
        "quality_level": quality_level,
        "feedback": feedback,
        "suggestions": feedback,
    }


# ============================================================
# 15. JOB READINESS ANALYSIS
# ============================================================

def calculate_job_readiness(user_skills, career_recommendations):
    """
    Estimate readiness from the best skill-match percentage.

    This is an indicative skill-based score, not a guarantee
    of employment or a complete assessment of job readiness.
    """
    normalized_skills = normalize_technical_skills(user_skills)

    if not normalized_skills:
        return {
            "score": 0,
            "readiness_score": 0,
            "level": "Beginner",
            "readiness_level": "Beginner",
            "feedback": (
                "Add your skills to receive a skill-based "
                "job readiness estimate."
            ),
        }

    if not career_recommendations:
        return {
            "score": 0,
            "readiness_score": 0,
            "level": "Beginner",
            "readiness_level": "Beginner",
            "feedback": (
                "More information is needed to estimate readiness."
            ),
        }

    best_match = max(
        (
            item.get("match_percentage", 0)
            for item in career_recommendations
        ),
        default=0
    )

    score = round(best_match)

    if score >= 80:
        level = "High"
        feedback = (
            "Your listed skills match many requirements of "
            "at least one suggested career. Practice projects "
            "and interview preparation can further help."
        )
    elif score >= 60:
        level = "Moderate"
        feedback = (
            "You have a foundation for a suggested career. "
            "Focus on the missing skills and build practical projects."
        )
    elif score >= 40:
        level = "Developing"
        feedback = (
            "Continue learning the core skills for your target career "
            "and demonstrate them through practical projects."
        )
    else:
        level = "Beginner"
        feedback = (
            "Start with the fundamentals of a target career, "
            "practice regularly, and build small projects."
        )

    return {
        "score": score,
        "readiness_score": score,
        "level": level,
        "readiness_level": level,
        "feedback": feedback,
    }
# ============================================================
# 16. PERSONALIZED CAREER GUIDANCE
# ============================================================

def generate_career_guidance(
    name,
    education,
    experience,
    user_skills,
    career_recommendations
):
    """
    Generate career guidance using the supplied profile,
    skills, and career recommendation results.
    """
    display_name = name.strip() if name else "Candidate"
    education_text = education.strip() if education else "Not provided"
    experience_text = experience.strip() if experience else "Not provided"

    normalized_skills = normalize_technical_skills(user_skills)

    guidance = []

    guidance.append(
        f"Hello {display_name}! Your personalized career guidance "
        "is based on the profile details and skills you provided."
    )

    guidance.append(
        f"Education: {education_text}. "
        f"Experience: {experience_text}."
    )

    if not normalized_skills:
        guidance.append(
            "Start by learning programming fundamentals and adding "
            "your current skills to your profile."
        )
    else:
        guidance.append(
            "Continue practicing your listed skills through exercises "
            "and practical projects."
        )

    if career_recommendations:
        best_career = career_recommendations[0]
        career_name = best_career.get("career", "your target career")
        match_percentage = best_career.get("match_percentage", 0)

        guidance.append(
            f"Your highest-ranked suggested career is {career_name}, "
            f"with a skill-match score of {match_percentage}%."
        )

        missing_skills = best_career.get("missing_skills", [])

        if missing_skills:
            guidance.append(
                "Focus on learning these missing skills: "
                + ", ".join(missing_skills)
                + "."
            )
        else:
            guidance.append(
                "Your listed skills match the required skills "
                "in this career's current project database."
            )

    guidance.append(
        "Build at least one practical project, document your work, "
        "and keep your resume updated."
    )

    guidance.append(
        "These recommendations are guidance based on your input, "
        "not a guarantee of employment."
    )

    return guidance


# ============================================================
# 17. DETAILED CAREER-SPECIFIC LEARNING ROADMAP
# ============================================================

def create_learning_roadmap(skill_gap_data):
    """
    Create learning steps for the missing skills of a career.
    """
    career = skill_gap_data.get("career", "")
    missing_skills = skill_gap_data.get("missing_skills", [])

    roadmap = []

    # Career-specific learning plans.
    ROADMAP_PLANS = {
        "Python Developer": {
            "Python": {
                "topics": (
                    "Python syntax, data types, conditions, loops, "
                    "functions and object-oriented programming."
                ),
                "practice": (
                    "Solve 10–15 beginner and intermediate Python problems."
                ),
                "project": "Build a simple Expense Tracker using Python.",
                "outcome": (
                    "Write and organize basic Python applications."
                ),
            },
            "Sql": {
                "topics": (
                    "SELECT queries, filtering, sorting, joins, "
                    "grouping and subqueries."
                ),
                "practice": (
                    "Practice SQL queries using a small student "
                    "or employee database."
                ),
                "project": "Build a Student Database Management System.",
                "outcome": (
                    "Retrieve and manipulate data using SQL."
                ),
            },
            "Git": {
                "topics": (
                    "Repositories, commits, branches, push, pull "
                    "and basic GitHub usage."
                ),
                "practice": (
                    "Create a repository and regularly commit "
                    "your practice programs."
                ),
                "project": "Upload one complete Python project to GitHub.",
                "outcome": (
                    "Manage and share code using Git."
                ),
            },
            "Oops": {
                "topics": (
                    "Classes, objects, constructors, inheritance "
                    "and polymorphism."
                ),
                "practice": (
                    "Create small programs using classes and objects."
                ),
                "project": "Build a Library Management System using OOP.",
                "outcome": (
                    "Structure Python applications using OOP."
                ),
            },
        },

        "Java Developer": {
            "Java": {
                "topics": (
                    "Java syntax, classes, objects, collections "
                    "and exception handling."
                ),
                "practice": "Solve Java programming problems regularly.",
                "project": "Build a Student Management System using Java.",
                "outcome": "Develop basic Java applications.",
            },
            "Sql": {
                "topics": (
                    "Queries, joins, grouping, constraints and subqueries."
                ),
                "practice": "Practice queries using sample databases.",
                "project": "Connect a Java application to a SQL database.",
                "outcome": (
                    "Work with databases from Java applications."
                ),
            },
            "Oops": {
                "topics": (
                    "Classes, objects, inheritance, polymorphism "
                    "and abstraction."
                ),
                "practice": (
                    "Implement small real-world examples using OOP."
                ),
                "project": "Create a Banking Management application.",
                "outcome": (
                    "Understand object-oriented application design."
                ),
            },
            "Git": {
                "topics": (
                    "Repositories, commits, branches and GitHub."
                ),
                "practice": "Maintain Java projects using Git.",
                "project": "Upload a Java project to GitHub.",
                "outcome": "Use basic version control.",
            },
        },

        "Software Developer": {
            "Python": {
                "topics": (
                    "Programming fundamentals, functions, OOP "
                    "and file handling."
                ),
                "practice": "Solve programming problems using Python.",
                "project": "Build a small Expense Tracker.",
                "outcome": "Develop basic software applications.",
            },
            "Java": {
                "topics": (
                    "Java fundamentals, OOP, collections "
                    "and exception handling."
                ),
                "practice": "Practice Java coding problems.",
                "project": "Build a Student Management application.",
                "outcome": (
                    "Develop structured applications using Java."
                ),
            },
            "Sql": {
                "topics": (
                    "Queries, joins, grouping, constraints "
                    "and database design."
                ),
                "practice": "Practice SQL using sample databases.",
                "project": "Create a database-backed application.",
                "outcome": "Work with application databases.",
            },
            "Git": {
                "topics": (
                    "Repositories, commits, branches and collaboration."
                ),
                "practice": "Use Git for every programming project.",
                "project": "Maintain a complete project on GitHub.",
                "outcome": "Understand basic software version control.",
            },
            "Oops": {
                "topics": (
                    "Classes, objects, inheritance, abstraction "
                    "and polymorphism."
                ),
                "practice": "Model real-world systems using OOP.",
                "project": "Build a Library Management System.",
                "outcome": "Design programs using OOP concepts.",
            },
        },

        "Full Stack Developer": {
            "Html": {
                "topics": (
                    "Semantic HTML, forms, tables and page structure."
                ),
                "practice": "Create different webpage layouts.",
                "project": "Build a responsive portfolio webpage.",
                "outcome": "Create structured web pages.",
            },
            "Css": {
                "topics": (
                    "Selectors, box model, Flexbox, Grid "
                    "and responsive design."
                ),
                "practice": (
                    "Recreate simple website layouts using CSS."
                ),
                "project": "Build a responsive portfolio website.",
                "outcome": "Create responsive interfaces.",
            },
            "Javascript": {
                "topics": (
                    "Variables, functions, DOM, events and API basics."
                ),
                "practice": "Build small interactive webpages.",
                "project": "Create an interactive To-Do application.",
                "outcome": "Add functionality to webpages.",
            },
            "React": {
                "topics": (
                    "Components, props, events and basic state management."
                ),
                "practice": "Create small React components.",
                "project": "Build a React task management application.",
                "outcome": "Develop basic React interfaces.",
            },
            "Node.Js": {
                "topics": (
                    "Node.js basics, modules, Express and REST APIs."
                ),
                "practice": "Create simple backend APIs.",
                "project": "Build a REST API for a task application.",
                "outcome": "Understand basic backend development.",
            },
            "Sql": {
                "topics": (
                    "Database tables, queries, joins and relationships."
                ),
                "practice": (
                    "Practice queries using a sample application database."
                ),
                "project": "Connect a web application to a SQL database.",
                "outcome": "Manage application data.",
            },
        },

        "Backend Developer": {
            "Python": {
                "topics": (
                    "Python fundamentals, OOP, functions and modules."
                ),
                "practice": "Solve backend-oriented Python problems.",
                "project": "Build a Python-based management application.",
                "outcome": "Write backend logic.",
            },
            "Flask": {
                "topics": (
                    "Routes, templates, forms, request handling and APIs."
                ),
                "practice": "Create small Flask applications.",
                "project": "Build a Flask REST API.",
                "outcome": "Develop basic Flask backends.",
            },
            "Sql": {
                "topics": (
                    "CRUD queries, joins, relationships and database design."
                ),
                "practice": "Create and query sample databases.",
                "project": "Build a database-backed Flask application.",
                "outcome": "Connect backend applications with databases.",
            },
            "Git": {
                "topics": "Repositories, commits, branches and GitHub.",
                "practice": "Use Git while developing backend projects.",
                "project": "Publish your Flask project on GitHub.",
                "outcome": "Understand version control for backend projects.",
            },
            "Rest Api": {
                "topics": "HTTP methods, JSON, endpoints and API testing.",
                "practice": "Create and test simple REST endpoints.",
                "project": (
                    "Build a REST API for a student management system."
                ),
                "outcome": "Create basic REST APIs.",
            },
        },
    }

    # Normalize career-specific roadmap keys.
    # These entries help match skills in a consistent format.
    CAREER_SKILL_KEY_ALIASES = {
        "sql": "Sql",
        "oops": "Oops",
        "html": "Html",
        "css": "Css",
        "javascript": "Javascript",
        "node.js": "Node.Js",
        "rest api": "Rest Api",
    }

    career_plans = ROADMAP_PLANS.get(career, {})

    for skill in missing_skills:
        normalized_skill = skill.strip().lower()
        skill_key = CAREER_SKILL_KEY_ALIASES.get(
            normalized_skill,
            skill.strip().title()
        )

        plan = career_plans.get(skill_key)

        # Fallback for skills without a specific plan.
        if not plan:
            plan = {
                "topics": (
                    f"Learn the core concepts and practical "
                    f"fundamentals of {skill}."
                ),
                "practice": (
                    f"Complete small exercises and practical tasks "
                    f"using {skill}."
                ),
                "project": (
                    f"Build a small project that demonstrates "
                    f"your {skill} skills."
                ),
                "outcome": (
                    f"Use {skill} confidently in basic practical work."
                ),
            }

        roadmap.append({
            "skill": skill,
            "steps": [
                f"What to learn: {plan['topics']}",
                f"Practice: {plan['practice']}",
                f"Mini-project: {plan['project']}",
                f"Expected outcome: {plan['outcome']}",
            ],
        })

    return roadmap
# ============================================================
# 18. EXTRACT TEXT FROM PDF RESUME
# ============================================================

def extract_text_from_pdf(pdf_path):
    """
    Extract readable text from a PDF resume.
    """
    try:
        reader = PdfReader(str(pdf_path))
        extracted_pages = []

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                extracted_pages.append(page_text)

        return "\n".join(extracted_pages).strip()

    except Exception as error:
        print(f"Error extracting PDF text: {error}")
        return ""


# ============================================================
# 19. VALIDATE RESUME FILE
# ============================================================

def is_allowed_resume(filename):
    """
    Check that the uploaded file has a PDF extension.
    """
    if not filename:
        return False

    return Path(filename).suffix.lower() in ALLOWED_RESUME_EXTENSIONS


# ============================================================
# 20. CLEAN FORM VALUES
# ============================================================

def clean_form_value(value):
    """
    Clean a value received from an HTML form.
    """
    if value is None:
        return ""

    return str(value).strip()


# ============================================================
# 21. GET SKILLS FROM FORM
# ============================================================

def get_form_skills(value):
    """
    Convert comma-separated form skills into a normalized list.
    """
    if not value:
        return []

    if isinstance(value, list):
        raw_skills = value
    else:
        raw_skills = re.split(r"[,;\n|]+", str(value))

    cleaned_skills = []

    for skill in raw_skills:
        skill = clean_form_value(skill)

        if skill:
            cleaned_skills.append(skill)

    return normalize_technical_skills(cleaned_skills)
# ============================================================
# 22. HOME PAGE
# ============================================================

@app.route("/")
def index():
    return render_template("index.html")


# ============================================================
# 23. ANALYZE PROFILE AND RESUME
# ============================================================

@app.route("/analyze", methods=["POST"])
def analyze():
    name = clean_form_value(request.form.get("name", ""))
    education = clean_form_value(request.form.get("education", ""))
    experience = clean_form_value(request.form.get("experience", ""))
    profile_skills = get_form_skills(
        request.form.get("skills", "")
    )

    resume_text = ""
    resume_skills = []
    resume_soft_skills = []

    # --------------------------------------------------------
    # Process optional resume upload
    # --------------------------------------------------------

    resume_file = request.files.get("resume")

    if resume_file and resume_file.filename:
        if not is_allowed_resume(resume_file.filename):
            return (
                "Invalid resume file. Please upload a PDF resume.",
                400
            )

        try:
            reader = PdfReader(resume_file.stream)
            extracted_pages = []

            for page in reader.pages:
                page_text = page.extract_text()

                if page_text:
                    extracted_pages.append(page_text)

            resume_text = "\n".join(extracted_pages).strip()

        except Exception:
            return (
                "The PDF could not be read. Please upload a valid PDF.",
                400
            )

        if not resume_text:
            return (
                "No readable text was found in the PDF. "
                "Please upload a text-based PDF resume.",
                400
            )

        # Extract technical skills from the Skills section only.
        resume_skills = extract_technical_skills(resume_text)

        # Soft skills are analyzed separately.
        resume_soft_skills = extract_soft_skills(resume_text)

    # --------------------------------------------------------
    # Combine profile and resume skills
    # --------------------------------------------------------

    combined_skills = combine_technical_skills(
        profile_skills,
        resume_skills
    )

    # --------------------------------------------------------
    # Recommend careers
    # --------------------------------------------------------

    career_recommendations = recommend_careers(combined_skills)

    top_career = (
        career_recommendations[0]["career"]
        if career_recommendations
        else None
    )

    # --------------------------------------------------------
    # Skill gap analysis
    # --------------------------------------------------------

    skill_gap_data = (
        analyze_skill_gap(combined_skills, top_career)
        if top_career
        else {
            "career": "",
            "required_skills": [],
            "matched_skills": [],
            "missing_skills": [],
            "total_required_skills": 0,
            "total_matched_skills": 0,
            "readiness_percentage": 0,
        }
    )
    skill_comparison = {
    "matched": skill_gap_data.get("matched_skills", []),
    "missing": skill_gap_data.get("missing_skills", []),
}

    # --------------------------------------------------------
    # Learning roadmap
    # --------------------------------------------------------

    learning_roadmap = create_learning_roadmap(skill_gap_data)

    # --------------------------------------------------------
    # Resume quality
    # --------------------------------------------------------

    resume_quality = calculate_resume_quality(
        name,
        education,
        experience,
        combined_skills,
        resume_text
    )

    # --------------------------------------------------------
    # Job readiness
    # --------------------------------------------------------

    job_readiness = calculate_job_readiness(
        combined_skills,
        career_recommendations
    )

    # --------------------------------------------------------
    # Personalized career guidance
    # --------------------------------------------------------

    guidance = generate_career_guidance(
        name,
        education,
        experience,
        combined_skills,
        career_recommendations
    )

    # --------------------------------------------------------
    # Career trend analysis
    # --------------------------------------------------------

    career_trend = (
        get_career_trend(top_career)
        if top_career
        else {
            "career": "",
            "demand": "Information unavailable",
            "growth": "Information unavailable",
            "future": "Add skills to receive career recommendations.",
        }
    )

    # --------------------------------------------------------
    # Example job titles for recommended careers
    # --------------------------------------------------------

    recommended_job_roles = get_recommended_job_roles(
        career_recommendations[:5]
    )

    # --------------------------------------------------------
    # Display results
    # --------------------------------------------------------
    # Compare entered skills with skills extracted from the PDF
    
    # --------------------------------------------------------
    # Display results
    # --------------------------------------------------------

    # Compare skills entered in the form with PDF skills.
    def normalize_skill_set(skills):
        return {
            str(skill).strip().lower()
            for skill in (skills or [])
            if str(skill).strip()
        }

    entered_skill_set = normalize_skill_set(profile_skills)
    resume_skill_set = normalize_skill_set(resume_skills)

    skill_comparison = {
        "matched": sorted(entered_skill_set & resume_skill_set),
        "only_profile": sorted(entered_skill_set - resume_skill_set),
        "only_resume": sorted(resume_skill_set - entered_skill_set),
    }

    return render_template(
        "result.html",
        name=name,
        education=education,
        experience=experience,
        profile_skills=profile_skills,
        resume_skills=resume_skills,
        resume_soft_skills=resume_soft_skills,
        combined_skills=combined_skills,
        career_recommendations=career_recommendations,
        top_career=top_career,
        skill_gap_data=skill_gap_data,
        skill_comparison=skill_comparison,
        learning_roadmap=learning_roadmap,
        resume_quality=resume_quality,
        job_readiness=job_readiness,
        guidance=guidance,
        personalized_guidance=guidance,
        career_trend=career_trend,
        recommended_job_roles=recommended_job_roles,
    )


# ============================================================
# 24. HANDLE LARGE FILE UPLOADS
# ============================================================

@app.errorhandler(RequestEntityTooLarge)
def handle_large_file(error):
    return (
        "The uploaded file is too large. "
        "Please upload a PDF smaller than 5 MB.",
        413
    )


# ============================================================
# 25. RUN THE FLASK APPLICATION
# ============================================================

if __name__ == "__main__":
    app.run(debug=True)