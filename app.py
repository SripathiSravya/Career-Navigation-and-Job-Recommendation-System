
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
# Canonical skill name -> words/phrases used to identify it
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
    "computer networks": ["computer networks", "networking", "computer networking"],
    "cybersecurity": ["cybersecurity", "cyber security", "information security"],
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
        "python", "sql", "pandas", "numpy", "data science", "machine learning"
    ],
    "Machine Learning Engineer": [
        "python", "machine learning", "pandas", "numpy", "sql"
    ],
    "AI Engineer": [
        "python", "artificial intelligence", "machine learning", "deep learning"
    ],
    "BI Analyst": [
        "sql", "excel", "power bi", "tableau", "data analysis"
    ],
    "Cloud Engineer": [
        "aws", "azure", "linux", "computer networks", "docker"
    ],
    "DevOps Engineer": ["linux", "docker", "kubernetes", "jenkins", "git"],
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
# This is sample project data, not live market information.
# ============================================================

CAREER_TRENDS = {
    "Python Developer": {
        "demand": "High", "growth": "Positive",
        "future": "Python is used in automation, web development and data applications."
    },
    "Java Developer": {
        "demand": "High", "growth": "Positive",
        "future": "Java remains useful for enterprise and backend applications."
    },
    "Software Developer": {
        "demand": "High", "growth": "Positive",
        "future": "Software development supports applications across many industries."
    },
    "Full Stack Developer": {
        "demand": "High", "growth": "Positive",
        "future": "Full-stack skills cover both user interfaces and server-side applications."
    },
    "Backend Developer": {
        "demand": "High", "growth": "Positive",
        "future": "Backend development supports APIs, business logic and data processing."
    },
    "Frontend Developer": {
        "demand": "High", "growth": "Positive",
        "future": "Frontend skills are useful for building accessible interactive websites."
    },
    "Web Developer": {
        "demand": "High", "growth": "Positive",
        "future": "Web development supports websites and browser-based applications."
    },
    "Mobile App Developer": {
        "demand": "High", "growth": "Positive",
        "future": "Mobile development supports applications for phones and tablets."
    },
    "Data Analyst": {
        "demand": "High", "growth": "Positive",
        "future": "Organizations use data analysis to support decisions."
    },
    "Data Scientist": {
        "demand": "High", "growth": "Positive",
        "future": "Data science combines statistics, programming and analytical methods."
    },
    "Machine Learning Engineer": {
        "demand": "High", "growth": "Positive",
        "future": "Machine learning engineering develops and maintains predictive systems."
    },
    "AI Engineer": {
        "demand": "High", "growth": "Positive",
        "future": "AI engineering applies artificial intelligence to practical problems."
    },
    "BI Analyst": {
        "demand": "High", "growth": "Positive",
        "future": "Business intelligence turns business data into reports and dashboards."
    },
    "Cloud Engineer": {
        "demand": "High", "growth": "Positive",
        "future": "Cloud engineering supports infrastructure, storage and deployment."
    },
    "DevOps Engineer": {
        "demand": "High", "growth": "Positive",
        "future": "DevOps practices help teams automate software delivery and operations."
    },
    "Cloud Developer": {
        "demand": "High", "growth": "Positive",
        "future": "Cloud developers build applications that use cloud services."
    },
    "Cybersecurity Analyst": {
        "demand": "High", "growth": "Positive",
        "future": "Security analysts help monitor systems and investigate security events."
    },
    "Security Engineer": {
        "demand": "High", "growth": "Positive",
        "future": "Security engineers design and improve technical security controls."
    },
    "Network Engineer": {
        "demand": "Moderate", "growth": "Positive",
        "future": "Network engineers configure, maintain and troubleshoot networks."
    },
    "Database Administrator": {
        "demand": "Moderate", "growth": "Positive",
        "future": "Database administrators maintain database availability and performance."
    },
    "Database Developer": {
        "demand": "Moderate", "growth": "Positive",
        "future": "Database developers design data structures and database solutions."
    },
    "Systems Analyst": {
        "demand": "Moderate", "growth": "Positive",
        "future": "Systems analysts connect business needs with technical solutions."
    },
    "QA/Test Engineer": {
        "demand": "High", "growth": "Positive",
        "future": "Software testing helps identify defects and improve product quality."
    },
    "Automation Test Engineer": {
        "demand": "High", "growth": "Positive",
        "future": "Test automation helps teams repeat checks more efficiently."
    },
    "UI/UX Designer": {
        "demand": "Moderate", "growth": "Positive",
        "future": "UI/UX design focuses on usable and understandable digital experiences."
    },
}


# ============================================================
# 4. EXAMPLE JOB TITLES
# These are role examples, not current vacancies.
# ============================================================

JOB_DATABASE = {
    "Python Developer": [
        "Python Developer", "Backend Python Developer", "Python Software Developer"
    ],
    "Java Developer": [
        "Java Developer", "Java Backend Developer", "Java Software Engineer"
    ],
    "Software Developer": [
        "Software Developer", "Application Developer", "Software Engineer"
    ],
    "Full Stack Developer": [
        "Full Stack Developer", "Web Application Developer", "Full Stack Software Engineer"
    ],
    "Backend Developer": [
        "Backend Developer", "API Developer", "Backend Software Engineer"
    ],
    "Frontend Developer": [
        "Frontend Developer", "React Developer", "UI Developer"
    ],
    "Web Developer": [
        "Web Developer", "Website Developer", "Web Application Developer"
    ],
    "Mobile App Developer": [
        "Android Developer", "Mobile Application Developer", "Mobile App Developer"
    ],
    "Data Analyst": [
        "Data Analyst", "Junior Data Analyst", "Business Data Analyst"
    ],
    "Data Scientist": [
        "Data Scientist", "Junior Data Scientist", "Data Science Associate"
    ],
    "Machine Learning Engineer": [
        "Machine Learning Engineer", "ML Engineer", "Junior ML Engineer"
    ],
    "AI Engineer": [
        "AI Engineer", "Artificial Intelligence Engineer", "Junior AI Engineer"
    ],
    "BI Analyst": [
        "Business Intelligence Analyst", "BI Analyst", "Business Data Analyst"
    ],
    "Cloud Engineer": [
        "Cloud Engineer", "Cloud Infrastructure Engineer", "Junior Cloud Engineer"
    ],
    "DevOps Engineer": [
        "DevOps Engineer", "Junior DevOps Engineer", "DevOps Associate"
    ],
    "Cloud Developer": [
        "Cloud Developer", "Cloud Application Developer", "Cloud Software Engineer"
    ],
    "Cybersecurity Analyst": [
        "Cybersecurity Analyst", "Security Analyst", "SOC Analyst"
    ],
    "Security Engineer": [
        "Security Engineer", "Information Security Engineer", "Cybersecurity Engineer"
    ],
    "Network Engineer": [
        "Network Engineer", "Network Administrator", "Junior Network Engineer"
    ],
    "Database Administrator": [
        "Database Administrator", "Database Support Engineer", "Junior DBA"
    ],
    "Database Developer": [
        "Database Developer", "SQL Developer", "Database Application Developer"
    ],
    "Systems Analyst": [
        "Systems Analyst", "Business Systems Analyst", "IT Systems Analyst"
    ],
    "QA/Test Engineer": [
        "QA Engineer", "Software Test Engineer", "Quality Analyst"
    ],
    "Automation Test Engineer": [
        "Automation Test Engineer", "Selenium Automation Engineer", "QA Automation Engineer"
    ],
    "UI/UX Designer": [
        "UI/UX Designer", "UX Designer", "UI Designer"
    ],
}


# ============================================================
# 5. SKILL NORMALIZATION AND EXTRACTION
# ============================================================

def _contains_skill(text, alias):
    """Match a phrase safely without matching it inside unrelated words."""
    text = text.lower()
    alias = alias.lower().strip()

    if not alias:
        return False

    # Standalone C can be written as "C", "C programming", etc.
    # Do not match the letter C inside words such as "communication".
    if alias == "c":
        return bool(re.search(r"(?<![a-z0-9+#])c(?![a-z0-9+#])", text))

    escaped = re.escape(alias)
    pattern = r"(?<![a-z0-9+#])" + escaped + r"(?![a-z0-9+#])"
    return bool(re.search(pattern, text, flags=re.IGNORECASE))


def normalize_technical_skills(skill_text):
    """Return canonical skill names found in the supplied text."""
    if not skill_text:
        return []

    text = str(skill_text).lower()
    found = []

    for canonical, aliases in SKILL_ALIASES.items():
        for alias in aliases:
            if _contains_skill(text, alias):
                found.append(canonical)
                break

    # Remove duplicates while preserving order.
    return list(dict.fromkeys(found))


def extract_technical_skills(resume_text):
    return normalize_technical_skills(resume_text)


def extract_soft_skills(resume_text):
    soft_skill_names = [
        "communication", "teamwork", "leadership", "time management",
        "project management", "presentation", "problem solving"
    ]
    found = normalize_technical_skills(resume_text)
    return [skill for skill in soft_skill_names if skill in found]


def combine_technical_skills(profile_skills, resume_skills):
    combined = list(profile_skills or []) + list(resume_skills or [])
    return sorted(set(combined), key=str.lower)


def compare_skills(profile_skills, resume_skills):
    profile = set(profile_skills or [])
    resume = set(resume_skills or [])

    matched = sorted(profile & resume, key=str.lower)
    only_profile = sorted(profile - resume, key=str.lower)
    only_resume = sorted(resume - profile, key=str.lower)

    # "common" is retained for compatibility with older code.
    return {
        "matched": matched,
        "common": matched,
        "only_profile": only_profile,
        "only_resume": only_resume,
    }


# ============================================================
# 6. CAREER RECOMMENDATIONS
# ============================================================

def recommend_careers(user_skills):
    user_skills = set(user_skills or [])
    recommendations = []

    for career, required_skills in CAREERS.items():
        required = list(required_skills)
        matched = [skill for skill in required if skill in user_skills]
        missing = [skill for skill in required if skill not in user_skills]

        percentage = round((len(matched) / len(required)) * 100) if required else 0

        recommendations.append({
            "career": career,
            "match": percentage,
            "percentage": percentage,
            "score": len(matched),
            "matched": matched,
            "missing": missing,
            "required": required,
        })

    # Sort consistently: match percentage, number of matches, then career name.
    recommendations.sort(
        key=lambda item: (
            -item["match"],
            -item["score"],
            item["career"].lower()
        )
    )
    return recommendations


def analyze_skill_gap(career, user_skills):
    required = CAREERS.get(career, [])
    user_skills = set(user_skills or [])

    matched = [skill for skill in required if skill in user_skills]
    missing = [skill for skill in required if skill not in user_skills]
    percentage = round((len(matched) / len(required)) * 100) if required else 0

    return {
        "career": career,
        "required": list(required),
        "matched": matched,
        "missing": missing,
        "percentage": percentage,
    }


# ============================================================
# 7. CAREER TREND ANALYSIS
# ============================================================

def get_career_trend(career):
    trend = CAREER_TRENDS.get(career, {
        "demand": "Moderate",
        "growth": "Positive",
        "future": "Research current job descriptions to understand the skills used in this career."
    })

    return {
        "career": career,
        "demand": trend["demand"],
        "growth": trend["growth"],
        "future": trend["future"],
    }


# ============================================================
# 8. CAREER-SPECIFIC LEARNING ROADMAP
# ============================================================

ROADMAP_PLANS = {
    "python": {
        "topics": "Syntax, data types, conditions, loops, functions and OOP",
        "practice": "Solve 10–15 beginner and intermediate Python problems.",
        "project": "Build an Expense Tracker using Python.",
        "outcome": "Write and organize basic Python applications."
    },
    "java": {
        "topics": "Syntax, classes, objects, collections and exception handling",
        "practice": "Solve Java programming problems regularly.",
        "project": "Build a Student Management System.",
        "outcome": "Develop basic Java applications."
    },
    "sql": {
        "topics": "SELECT, filtering, joins, grouping, subqueries and constraints",
        "practice": "Practice queries on a sample database.",
        "project": "Build a Student Database Management System.",
        "outcome": "Retrieve and manipulate relational data."
    },
    "git": {
        "topics": "Repositories, commits, branches, push, pull and GitHub",
        "practice": "Track your practice code using Git.",
        "project": "Publish a complete project on GitHub.",
        "outcome": "Manage code with version control."
    },
    "oops": {
        "topics": "Classes, objects, constructors, inheritance and polymorphism",
        "practice": "Create small programs using classes and objects.",
        "project": "Build a Library Management System.",
        "outcome": "Structure programs using object-oriented concepts."
    },
    "html": {
        "topics": "Semantic elements, forms, links, tables and page structure",
        "practice": "Create several static webpages.",
        "project": "Build a personal portfolio webpage.",
        "outcome": "Create well-structured web pages."
    },
    "css": {
        "topics": "Selectors, box model, Flexbox, Grid and responsive design",
        "practice": "Recreate simple website layouts.",
        "project": "Build a responsive portfolio website.",
        "outcome": "Create responsive interfaces."
    },
    "javascript": {
        "topics": "Variables, functions, DOM, events and API basics",
        "practice": "Build small interactive webpages.",
        "project": "Create an interactive To-Do application.",
        "outcome": "Add dynamic behaviour to webpages."
    },
    "react": {
        "topics": "Components, props, events and state management",
        "practice": "Create small React components.",
        "project": "Build a React task management application.",
        "outcome": "Develop component-based interfaces."
    },
    "node.js": {
        "topics": "Node.js, modules, Express and REST APIs",
        "practice": "Create simple backend APIs.",
        "project": "Build a task-management REST API.",
        "outcome": "Understand basic backend development."
    },
    "flask": {
        "topics": "Routes, templates, forms, requests and APIs",
        "practice": "Create small Flask applications.",
        "project": "Build a Flask REST API.",
        "outcome": "Develop basic Python web backends."
    },
    "api": {
        "topics": "HTTP methods, JSON, endpoints, status codes and validation",
        "practice": "Create and test simple REST endpoints.",
        "project": "Build a Student Management REST API.",
        "outcome": "Design and test basic APIs."
    },
    "pandas": {
        "topics": "DataFrames, filtering, grouping, missing values and cleaning",
        "practice": "Clean and analyze sample datasets.",
        "project": "Perform customer or sales data analysis.",
        "outcome": "Prepare datasets for analysis."
    },
    "numpy": {
        "topics": "Arrays, indexing, mathematical and numerical operations",
        "practice": "Perform numerical calculations on sample data.",
        "project": "Create a statistical analysis notebook.",
        "outcome": "Understand numerical computing basics."
    },
    "data science": {
        "topics": "Data cleaning, exploration, visualization and basic statistics",
        "practice": "Perform exploratory data analysis.",
        "project": "Analyze a public dataset and document your findings.",
        "outcome": "Understand the basic data science workflow."
    },
    "data analysis": {
        "topics": "Data cleaning, exploration, charts and interpretation",
        "practice": "Analyze a real-world business dataset.",
        "project": "Create an end-to-end sales analysis report.",
        "outcome": "Turn data into useful business insights."
    },
    "machine learning": {
        "topics": "Regression, classification, clustering and model evaluation",
        "practice": "Train and compare simple ML models.",
        "project": "Build a prediction model using a public dataset.",
        "outcome": "Understand the basic machine learning workflow."
    },
    "artificial intelligence": {
        "topics": "AI fundamentals, search, reasoning and machine learning basics",
        "practice": "Implement small AI-related exercises.",
        "project": "Build a simple intelligent application.",
        "outcome": "Understand introductory AI techniques."
    },
    "deep learning": {
        "topics": "Neural networks, layers, training and basic image/text models",
        "practice": "Train a simple neural network.",
        "project": "Build an image classification prototype.",
        "outcome": "Understand basic deep learning."
    },
    "excel": {
        "topics": "Formulas, functions, sorting, filtering, charts and PivotTables",
        "practice": "Analyze sample business spreadsheets.",
        "project": "Create a sales dashboard in Excel.",
        "outcome": "Perform spreadsheet-based business analysis."
    },
    "power bi": {
        "topics": "Data import, Power Query, relationships and dashboards",
        "practice": "Create interactive reports.",
        "project": "Build a business performance dashboard.",
        "outcome": "Create basic BI dashboards."
    },
    "tableau": {
        "topics": "Data connections, charts, filters and dashboards",
        "practice": "Create visual reports using sample data.",
        "project": "Build a sales analytics dashboard.",
        "outcome": "Understand data visualization."
    },
    "aws": {
        "topics": "EC2, S3, IAM and basic cloud networking",
        "practice": "Explore basic AWS resources and permissions.",
        "project": "Deploy a simple web application on AWS.",
        "outcome": "Understand basic AWS services."
    },
    "azure": {
        "topics": "Azure compute, storage, identity and networking",
        "practice": "Explore basic Azure resources.",
        "project": "Deploy a simple application on Azure.",
        "outcome": "Understand basic Azure services."
    },
    "linux": {
        "topics": "Commands, files, permissions, processes and logs",
        "practice": "Practice Linux commands in a safe virtual environment.",
        "project": "Set up a basic Linux server environment.",
        "outcome": "Work comfortably with Linux systems."
    },
    "computer networks": {
        "topics": "TCP/IP, subnetting, routing, switching, DNS and ports",
        "practice": "Solve basic networking problems.",
        "project": "Design a small office network.",
        "outcome": "Understand fundamental network infrastructure."
    },
    "docker": {
        "topics": "Images, containers, Dockerfiles and volumes",
        "practice": "Containerize a simple application.",
        "project": "Dockerize a Flask application.",
        "outcome": "Package applications using containers."
    },
    "kubernetes": {
        "topics": "Pods, deployments, services and cluster concepts",
        "practice": "Deploy containers to a local learning cluster.",
        "project": "Deploy a small web application using Kubernetes.",
        "outcome": "Understand container orchestration basics."
    },
    "jenkins": {
        "topics": "Jobs, pipelines, builds and automated testing",
        "practice": "Create a simple continuous integration pipeline.",
        "project": "Build a pipeline that tests a sample project.",
        "outcome": "Understand basic CI workflows."
    },
    "testing": {
        "topics": "Test cases, scenarios, defect reporting and execution",
        "practice": "Write test cases for a simple application.",
        "project": "Test a web application and report defects.",
        "outcome": "Understand the software testing process."
    },
    "selenium": {
        "topics": "WebDriver, locators, waits and browser automation",
        "practice": "Automate a login form and simple workflows.",
        "project": "Build Selenium tests for a sample website.",
        "outcome": "Automate basic browser tests."
    },
    "cybersecurity": {
        "topics": "Security fundamentals, threats, vulnerabilities and controls",
        "practice": "Analyze common security scenarios in a legal lab.",
        "project": "Create a basic cybersecurity risk assessment.",
        "outcome": "Understand fundamental cybersecurity concepts."
    },
    "network security": {
        "topics": "Firewalls, secure protocols, access control and monitoring",
        "practice": "Review sample network security configurations.",
        "project": "Design a basic secure network.",
        "outcome": "Understand network security fundamentals."
    },
    "penetration testing": {
        "topics": "Authorization, reconnaissance, vulnerability assessment and reporting",
        "practice": "Use intentionally vulnerable training labs only.",
        "project": "Write a report about findings in an authorized lab.",
        "outcome": "Understand responsible security testing."
    },
    "mongodb": {
        "topics": "Documents, collections, CRUD operations and data modeling",
        "practice": "Create and query MongoDB collections.",
        "project": "Build a simple MongoDB-backed application.",
        "outcome": "Understand document-based database operations."
    },
    "business analysis": {
        "topics": "Requirements gathering, process analysis and documentation",
        "practice": "Analyze simple business requirements.",
        "project": "Document requirements for a software system.",
        "outcome": "Understand basic business analysis techniques."
    },
    "problem solving": {
        "topics": "Logical reasoning, decomposition and solution design",
        "practice": "Solve programming problems and case studies.",
        "project": "Analyze a problem and document a practical solution.",
        "outcome": "Improve structured problem-solving skills."
    },
    "figma": {
        "topics": "Frames, components, layouts, prototypes and design systems",
        "practice": "Recreate simple mobile and web interfaces.",
        "project": "Design a complete mobile application prototype.",
        "outcome": "Create interactive UI designs."
    },
    "ui/ux": {
        "topics": "User research, wireframes, user flows and usability principles",
        "practice": "Create wireframes for a common application.",
        "project": "Design a student application experience.",
        "outcome": "Understand the basic UI/UX design process."
    },
    "communication": {
        "topics": "Clear writing, active listening and explaining technical ideas",
        "practice": "Explain a small project to another person.",
        "project": "Prepare and present a project summary.",
        "outcome": "Communicate technical information clearly."
    },
}


def _roadmap_key(skill):
    """Normalize skills so roadmap lookups are consistent."""
    skill = str(skill).strip().lower()
    aliases = {
        "oop": "oops",
        "object oriented programming": "oops",
        "c++": "c++",
        "ml": "machine learning",
        "ai": "artificial intelligence",
        "rest api": "api",
        "restful api": "api",
        "nodejs": "node.js",
        "node js": "node.js",
        "powerbi": "power bi",
        "cyber security": "cybersecurity",
        "data analytics": "data analysis",
        "user experience": "ui/ux",
        "user interface": "ui/ux",
        "manual testing": "testing",
        "automation testing": "testing",
        "test automation": "testing",
    }
    return aliases.get(skill, skill)


def create_learning_roadmap(career, missing_skills):
    roadmap = []

    for skill in missing_skills:
        key = _roadmap_key(skill)
        plan = ROADMAP_PLANS.get(key)

        if not plan:
            plan = {
                "topics": f"Learn the core concepts and practical fundamentals of {skill}.",
                "practice": f"Complete exercises and practical tasks using {skill}.",
                "project": f"Build a small project demonstrating your {skill} skills.",
                "outcome": f"Use {skill} confidently in basic practical work."
            }

        roadmap.append({
            "skill": skill,
            "steps": [
                f"What to learn: {plan['topics']}",
                f"Practice: {plan['practice']}",
                f"Mini-project: {plan['project']}",
                f"Expected outcome: {plan['outcome']}",
            ]
        })

    # Add a career-specific project so the roadmap has a practical goal.
    career_projects = {
        "Python Developer": "Build a Python Expense Tracker.",
        "Java Developer": "Build a Student Management System in Java.",
        "Software Developer": "Build and document a small software application.",
        "Full Stack Developer": "Build a full-stack task management website.",
        "Backend Developer": "Build a REST API with database integration.",
        "Frontend Developer": "Build a responsive React dashboard.",
        "Web Developer": "Build a multi-page responsive portfolio.",
        "Mobile App Developer": "Build a simple Android task management app.",
        "Data Analyst": "Analyze a sales dataset and create a dashboard.",
        "Data Scientist": "Complete an exploratory data analysis project.",
        "Machine Learning Engineer": "Build and evaluate a prediction model.",
        "AI Engineer": "Build a small AI-powered prototype.",
        "BI Analyst": "Create an interactive business dashboard.",
        "Cloud Engineer": "Deploy a web application to a cloud platform.",
        "DevOps Engineer": "Create a containerized application pipeline.",
        "Cloud Developer": "Build and deploy a cloud-ready API.",
        "Cybersecurity Analyst": "Create a sample security log analysis report.",
        "Security Engineer": "Design a basic secure application architecture.",
        "Network Engineer": "Design and document a small office network.",
        "Database Administrator": "Create a database backup and maintenance plan.",
        "Database Developer": "Design a relational database for an application.",
        "Systems Analyst": "Write requirements for a software system.",
        "QA/Test Engineer": "Create test cases and a defect report.",
        "Automation Test Engineer": "Automate a sample website test workflow.",
        "UI/UX Designer": "Create a prototype and a short design case study.",
    }

    roadmap.append({
        "skill": "Career Project",
        "steps": [
            "What to learn: Apply the skills required for your selected career.",
            "Practice: Divide the work into small, testable tasks.",
            f"Mini-project: {career_projects.get(career, 'Build a project related to your career.')}",
            "Expected outcome: Have a project you can demonstrate and explain."
        ]
    })

    # Keep the roadmap manageable and remove duplicate skill entries.
    seen = set()
    unique_roadmap = []

    for item in roadmap:
        key = item["skill"].lower()
        if key not in seen:
            seen.add(key)
            unique_roadmap.append(item)

    return unique_roadmap[:6]


# ============================================================
# 9. RECOMMENDED JOB ROLES
# Dashboard expects a grouped structure with career, match, roles.
# ============================================================

def recommend_jobs(career):
    return JOB_DATABASE.get(career, [])


def recommend_jobs_for_top_careers(career_recommendations, limit=3):
    grouped_jobs = []

    for item in (career_recommendations or [])[:limit]:
        career = item.get("career")
        grouped_jobs.append({
            "career": career,
            "match": item.get("match", item.get("percentage", 0)),
            "roles": recommend_jobs(career),
        })

    return grouped_jobs


# ============================================================
# 10. RESUME QUALITY ANALYSIS
# ============================================================

def calculate_resume_quality(
    resume_text, resume_skills, name, education, experience
):
    text = (resume_text or "").strip()
    lower_text = text.lower()
    checks = []
    score = 0

    # Resume content
    if len(text) >= 500:
        score += 20
        checks.append({
            "name": "Resume content",
            "status": "Good",
            "detail": "The resume contains a useful amount of text."
        })
    else:
        score += 8
        checks.append({
            "name": "Resume content",
            "status": "Needs improvement",
            "detail": "Add relevant details about education, skills and projects."
        })

    # Technical skills
    if len(resume_skills) >= 5:
        score += 20
        checks.append({
            "name": "Technical skills",
            "status": "Good",
            "detail": f"{len(resume_skills)} recognized skills were identified."
        })
    elif len(resume_skills) >= 2:
        score += 12
        checks.append({
            "name": "Technical skills",
            "status": "Fair",
            "detail": "Add more relevant skills that you can demonstrate."
        })
    else:
        score += 5
        checks.append({
            "name": "Technical skills",
            "status": "Needs improvement",
            "detail": "Include technical skills that accurately reflect your ability."
        })

    # Education
    if education and education.strip():
        score += 10
        checks.append({
            "name": "Education",
            "status": "Present",
            "detail": "Education information was provided."
        })
    else:
        checks.append({
            "name": "Education",
            "status": "Missing",
            "detail": "Add your degree and relevant education details."
        })

    if re.search(r"\b(university|college|institute)\b", lower_text):
        score += 5
        checks.append({
            "name": "Institution",
            "status": "Present",
            "detail": "The resume appears to mention an educational institution."
        })
    else:
        checks.append({
            "name": "Institution",
            "status": "Optional improvement",
            "detail": "Consider including your college or university."
        })

    # Contact details
    if re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", text):
        score += 10
        checks.append({
            "name": "Email",
            "status": "Present",
            "detail": "An email address was detected."
        })
    else:
        checks.append({
            "name": "Email",
            "status": "Missing",
            "detail": "Add a professional email address to your resume."
        })

    if re.search(r"(\+?\d[\d\s().-]{7,}\d)", text):
        score += 5
        checks.append({
            "name": "Phone number",
            "status": "Present",
            "detail": "A possible phone number was detected."
        })
    else:
        checks.append({
            "name": "Phone number",
            "status": "Missing",
            "detail": "Consider including a contact phone number."
        })

    if name and name.strip():
        score += 5
        checks.append({
            "name": "Name",
            "status": "Present",
            "detail": "Your name was provided in the form."
        })
    else:
        checks.append({
            "name": "Name",
            "status": "Missing",
            "detail": "Add your name to the resume."
        })

    if experience and experience.strip():
        score += 10
        checks.append({
            "name": "Experience",
            "status": "Present",
            "detail": "Experience information was provided."
        })
    else:
        checks.append({
            "name": "Experience",
            "status": "Optional improvement",
            "detail": "Include experience, internships, or relevant academic work."
        })

    if re.search(r"\b(project|projects)\b", lower_text):
        score += 15
        checks.append({
            "name": "Projects",
            "status": "Present",
            "detail": "Project information was detected."
        })
    else:
        checks.append({
            "name": "Projects",
            "status": "Needs improvement",
            "detail": "Add academic or personal projects with your contribution."
        })

    score = min(score, 100)

    if score >= 80:
        label = "Strong"
    elif score >= 60:
        label = "Good"
    elif score >= 40:
        label = "Fair"
    else:
        label = "Needs Improvement"

    return {
        "score": score,
        "checks": checks,
        "label": label,
    }


# ============================================================
# 11. JOB READINESS
# This is a heuristic based on skills and experience, not a hiring
# prediction or a guarantee of employment.
# ============================================================

def calculate_job_readiness(career, user_skills, experience):
    required = CAREERS.get(career, [])
    user_skills = set(user_skills or [])
    matched = [skill for skill in required if skill in user_skills]
    missing = [skill for skill in required if skill not in user_skills]

    skill_score = round(
        (len(matched) / len(required)) * 80
    ) if required else 0

    experience_text = (experience or "").strip().lower()

    if any(word in experience_text for word in [
        "experienced", "years", "year", "professional", "working"
    ]):
        experience_score = 20
    elif any(word in experience_text for word in [
        "internship", "intern", "project", "training"
    ]):
        experience_score = 15
    else:
        # Fresher status is not treated as zero readiness.
        experience_score = 10

    score = min(skill_score + experience_score, 100)

    if score >= 80:
        label = "High"
        advice = "You have a strong skill match. Strengthen your portfolio and prepare to explain your projects."
    elif score >= 60:
        label = "Good"
        advice = "You have a useful starting point. Practice your missing skills and build one career-related project."
    elif score >= 40:
        label = "Developing"
        advice = "Focus on the most important missing skills, complete practical exercises and document your progress."
    else:
        label = "Beginner"
        advice = "Start with the fundamentals of this career, practice consistently and complete a small guided project."

    if missing:
        advice += " Skills to work on next: " + ", ".join(missing[:3]) + "."

    return {
        "score": score,
        "label": label,
        "skill_score": skill_score,
        "experience_score": experience_score,
        "advice": advice,
    }


# ============================================================
# 12. PERSONALIZED CAREER GUIDANCE
# ============================================================

def create_personalized_guidance(
    career, skill_gap_data, resume_quality, job_readiness
):
    guidance = []

    if career:
        guidance.append(
            f"Your current strongest skill-based match is {career}. "
            "Treat this as a starting point for exploring the career."
        )

    matched = skill_gap_data.get("matched", [])
    missing = skill_gap_data.get("missing", [])

    if matched:
        guidance.append(
            "Skills already matching this career: " + ", ".join(matched) + "."
        )
    else:
        guidance.append(
            "Start by learning the core skills listed for this career."
        )

    if missing:
        guidance.append(
            "Prioritize these missing skills: " + ", ".join(missing[:4]) + "."
        )
    else:
        guidance.append(
            "Your current recognized skills cover the listed skills for this career. "
            "Build projects to demonstrate practical ability."
        )

    if resume_quality.get("score", 0) < 70:
        guidance.append(
            "Improve your resume by adding clear project descriptions, "
            "relevant skills, contact details and measurable contributions."
        )
    else:
        guidance.append(
            "Review your resume for clarity and make sure every listed skill "
            "is supported by experience, coursework or projects."
        )

    guidance.append(
        f"Your estimated job-readiness score is {job_readiness.get('score', 0)}%. "
        "Use it as a planning guide, not as a guarantee of employment."
    )

    guidance.append(
        "Build at least one relevant project, upload it to a code repository "
        "when appropriate, and practice explaining your decisions."
    )

    return guidance


# ============================================================
# 13. HOME PAGE
# ============================================================

@app.route("/")
def home():
    return render_template("index.html")


# ============================================================
# 14. UPLOAD SIZE ERROR
# ============================================================

@app.errorhandler(RequestEntityTooLarge)
def handle_large_file(error):
    return render_template(
        "index.html",
        error_messages=["The uploaded file is too large. Please upload a PDF smaller than 5 MB."]
    ), 413


# ============================================================
# 15. ANALYZE FORM AND RESUME
# ============================================================

@app.route("/analyze", methods=["POST"])
def analyze():
    name = request.form.get("name", "").strip()
    education = request.form.get("education", "").strip()
    experience = request.form.get("experience", "").strip()
    profile_skills_text = request.form.get("skills", "").strip()

    error_messages = []

    if not name:
        error_messages.append("Please enter your name.")

    if not education:
        error_messages.append("Please enter your education.")

    if not profile_skills_text:
        error_messages.append("Please enter your skills.")

    resume_file = request.files.get("resume")

    if not resume_file or not resume_file.filename:
        error_messages.append("Please upload your resume as a PDF.")

    if error_messages:
        return render_template(
            "index.html",
            error_messages=error_messages
        )

    extension = Path(resume_file.filename).suffix.lower()

    if extension not in ALLOWED_RESUME_EXTENSIONS:
        return render_template(
            "index.html",
            error_messages=["Only PDF resumes are supported."]
        )

    try:
        reader = PdfReader(resume_file.stream)

        if reader.is_encrypted:
            return render_template(
                "index.html",
                error_messages=[
                    "This PDF is password-protected. Please upload an unlocked PDF."
                ]
            )

        resume_text_parts = []

        for page in reader.pages:
            resume_text_parts.append(page.extract_text() or "")

        resume_text = "\n".join(resume_text_parts).strip()

    except Exception:
        return render_template(
            "index.html",
            error_messages=[
                "The PDF could not be read. Please upload a valid, text-readable PDF."
            ]
        )

    if not resume_text:
        return render_template(
            "index.html",
            error_messages=[
                "No readable text was found in the PDF. If it is a scanned image, "
                "use a text-based PDF or add OCR support."
            ]
        )

    # Extract recognized skills from the user's form and resume.
    profile_skills = normalize_technical_skills(profile_skills_text)
    resume_skills = extract_technical_skills(resume_text)
    resume_soft_skills = extract_soft_skills(resume_text)

    combined_skills = combine_technical_skills(
        profile_skills,
        resume_skills
    )

    if not combined_skills:
        return render_template(
            "index.html",
            error_messages=[
                "No recognized skills were found. Enter skills such as Python, "
                "Java, SQL, HTML, CSS, Excel or other relevant skills."
            ]
        )

    # Compare skills supplied in the form with skills extracted from the resume.
    skill_comparison = compare_skills(
        profile_skills,
        resume_skills
    )

    # All 25 career recommendations, sorted by match percentage.
    career_recommendations = recommend_careers(combined_skills)

    # Choose the top result from the transparent skill-match calculation.
    top_career = career_recommendations[0]["career"]

    skill_gap_data = analyze_skill_gap(
        top_career,
        combined_skills
    )

    career_trend = get_career_trend(top_career)

    learning_roadmap = create_learning_roadmap(
        top_career,
        skill_gap_data["missing"]
    )

    # The dashboard expects one group per career, each with a roles list.
    recommended_job_roles = recommend_jobs_for_top_careers(
        career_recommendations,
        limit=3
    )

    # Also supply the top career's titles separately if the template uses them.
    job_recommendations = recommend_jobs(top_career)

    resume_quality = calculate_resume_quality(
        resume_text,
        resume_skills,
        name,
        education,
        experience
    )

    job_readiness = calculate_job_readiness(
        top_career,
        combined_skills,
        experience
    )

    personalized_guidance = create_personalized_guidance(
        top_career,
        skill_gap_data,
        resume_quality,
        job_readiness
    )

    return render_template(
        "result.html",
        name=name,
        education=education,
        experience=experience,
        profile_skills=profile_skills,
        resume_skills=resume_skills,
        resume_soft_skills=resume_soft_skills,
        combined_skills=combined_skills,
        skill_comparison=skill_comparison,
        career_recommendations=career_recommendations,
        top_career=top_career,
        skill_gap_data=skill_gap_data,
        career_trend=career_trend,
        learning_roadmap=learning_roadmap,
        recommended_job_roles=recommended_job_roles,
        job_recommendations=job_recommendations,
        resume_quality=resume_quality,
        job_readiness=job_readiness,
        personalized_guidance=personalized_guidance,
    )


# ============================================================
# 16. RUN APPLICATION
# ============================================================

if __name__ == "__main__":
    app.run(debug=True)
