"""
Seed data script for SkillBridge.
Populates admin, sample student, career roles, skills, requirement mappings, and verified learning resources.
"""

from app import create_app
from app.extensions import db
from app.models.user import User, StudentProfile
from app.models.career import CareerRole, RoleSkillRequirement
from app.models.skill import Skill, StudentSkill
from app.models.resource import LearningResource, StudentProgress
from app.services.skill_gap_service import calculate_skill_gap
from app.services.roadmap_service import generate_learning_roadmap

def seed_database():
    app = create_app()
    with app.app_context():
        print("Initializing database tables...")
        db.create_all()

        # 1. ADMIN USER
        admin = User.query.filter_by(email='admin@skillbridge.edu').first()
        if not admin:
            admin = User(
                email='admin@skillbridge.edu',
                full_name='System Administrator',
                role='admin',
                is_active=True
            )
            admin.set_password('adminpassword123')
            db.session.add(admin)
            print("Created Admin account: admin@skillbridge.edu / adminpassword123")

        # 2. SKILLS CATALOG
        skills_data = [
            # Programming & Foundations
            ('SK-PYT', 'Python', 'Programming', 'High-level interpreted language for general computing, backend, data science and AI.', 'code'),
            ('SK-JAV', 'Java', 'Programming', 'Robust object-oriented programming language for enterprise software and Android.', 'code'),
            ('SK-JS', 'JavaScript', 'Frontend', 'Dynamic scripting language enabling interactive web client interfaces.', 'javascript'),
            ('SK-TS', 'TypeScript', 'Frontend', 'Typed superset of JavaScript providing static type definitions.', 'code'),
            ('SK-HTML', 'HTML5', 'Frontend', 'Hypertext markup language structuring contemporary web content.', 'html'),
            ('SK-CSS', 'CSS3', 'Frontend', 'Cascading style sheets for responsive layouts, flexbox, grid, and animations.', 'css'),

            # Frameworks & Backend
            ('SK-FLK', 'Flask', 'Backend', 'Lightweight WSGI Python microframework for web APIs and rapid web services.', 'webhook'),
            ('SK-DJA', 'Django', 'Backend', 'High-level Python web framework encouraging clean design and rapid prototyping.', 'webhook'),
            ('SK-SPR', 'Spring Boot', 'Backend', 'Enterprise Java framework for production-ready stand-alone applications.', 'hub'),
            ('SK-NOD', 'Node.js', 'Backend', 'Asynchronous event-driven JavaScript runtime environment.', 'terminal'),
            ('SK-EXP', 'Express.js', 'Backend', 'Minimalist web framework for Node.js REST API backends.', 'terminal'),
            ('SK-REA', 'React.js', 'Frontend', 'Declarative component-based library for building interactive user interfaces.', 'web'),
            ('SK-API', 'RESTful APIs', 'Backend', 'Architectural style for networked hypermedia systems and HTTP endpoints.', 'api'),

            # Databases & Persistence
            ('SK-SQL', 'SQL Fundamentals', 'Database', 'Standardized query language for relational database management.', 'database'),
            ('SK-PGS', 'PostgreSQL', 'Database', 'Advanced open-source object-relational database system.', 'database'),
            ('SK-MDB', 'MongoDB', 'Database', 'Document-oriented NoSQL database for flexible JSON-like documents.', 'database'),

            # DevOps & Cloud
            ('SK-GIT', 'Git & GitHub', 'DevOps', 'Distributed version control system for tracking source code changes.', 'fork_right'),
            ('SK-DOC', 'Docker', 'DevOps', 'Platform for developing, shipping, and running applications in containers.', 'inventory_2'),
            ('SK-K8S', 'Kubernetes', 'DevOps', 'Automated container orchestration and microservice management.', 'anchor'),
            ('SK-AWS', 'AWS Cloud Foundations', 'Cloud', 'Comprehensive cloud computing platform with EC2, S3, RDS and Lambda.', 'cloud'),
            ('SK-LNX', 'Linux & Bash', 'DevOps', 'Open-source Unix operating system and command line shell scripting.', 'terminal'),

            # Data Science & AI
            ('SK-DA', 'Data Analysis with Pandas', 'Data Science', 'Data manipulation, dataframe inspection, cleaning and aggregation.', 'table_chart'),
            ('SK-ML', 'Machine Learning with Scikit-Learn', 'Machine Learning', 'Supervised and unsupervised ML algorithms, classification and regression.', 'psychology'),
            ('SK-GEN', 'Generative AI & LLMs', 'Artificial Intelligence', 'Large language models, prompt engineering, fine-tuning and embeddings.', 'auto_awesome'),
            ('SK-CYB', 'Network Security Basics', 'Cybersecurity', 'Firewalls, network protocols, cryptography and vulnerability mitigation.', 'security')
        ]

        skill_map = {}
        for code, name, category, desc, icon in skills_data:
            skill = Skill.query.filter_by(code=code).first()
            if not skill:
                skill = Skill(code=code, name=name, category=category, description=desc, icon_name=icon)
                db.session.add(skill)
            skill_map[code] = skill
        db.session.flush()
        print(f"Verified {len(skills_data)} skills in catalog.")

        # 3. CAREER ROLES
        roles_data = [
            (
                'CR-101', 'Web Developer', 'Web Development',
                'Builds modern responsive web applications using frontend technologies, REST APIs, and relational databases.',
                'Beginner', '₹5 - ₹10 LPA', 'High'
            ),
            (
                'CR-102', 'Python Developer', 'Web & Backend',
                'Designs scalable backend services, RESTful APIs, data access layers, and automation workflows using Python.',
                'Intermediate', '₹6 - ₹15 LPA', 'Very High'
            ),
            (
                'CR-103', 'Java Developer', 'Enterprise Backend',
                'Architects high-performance enterprise systems, microservices, and secure backends with Java and Spring Boot.',
                'Intermediate', '₹7 - ₹16 LPA', 'High'
            ),
            (
                'CR-104', 'Data Analyst', 'Data & Analytics',
                'Inspects, cleans, transforms and models structured datasets to discover business insights and build dashboard KPIs.',
                'Beginner', '₹5 - ₹11 LPA', 'High'
            ),
            (
                'CR-105', 'Full Stack Developer', 'Web Development',
                'Masters both frontend client interfaces and backend services, database design, and end-to-end integration.',
                'Advanced', '₹8 - ₹18 LPA', 'Very High'
            ),
            (
                'CR-106', 'AI / ML Engineer', 'Artificial Intelligence',
                'Develops machine learning models, statistical pipelines, neural networks, and scalable inference services.',
                'Advanced', '₹10 - ₹24 LPA', 'Very High'
            ),
            (
                'CR-107', 'Cloud & DevOps Engineer', 'Cloud & DevOps',
                'Automates deployment pipelines, containerizes microservices with Docker/Kubernetes, and manages cloud infrastructure.',
                'Intermediate', '₹8 - ₹18 LPA', 'Very High'
            ),
            (
                'CR-108', 'Cybersecurity Analyst', 'Cybersecurity',
                'Protects computer systems and networks against intrusions, audits vulnerabilities, and enforces security compliance.',
                'Intermediate', '₹7 - ₹16 LPA', 'Growing'
            ),
            (
                'CR-109', 'Data Scientist', 'Data & Analytics',
                'Utilizes advanced mathematics, statistics, and machine learning to build predictive models from big data.',
                'Advanced', '₹10 - ₹22 LPA', 'High'
            ),
            (
                'CR-110', 'Generative AI Developer', 'Artificial Intelligence',
                'Builds intelligent agentic applications, RAG pipelines, and LLM integrations with prompt engineering.',
                'Advanced', '₹12 - ₹25 LPA', 'Emerging'
            )
        ]

        role_map = {}
        for code, title, category, desc, diff, salary, demand in roles_data:
            role = CareerRole.query.filter_by(code=code).first()
            if not role:
                role = CareerRole(
                    code=code, title=title, category=category,
                    description=desc, difficulty_level=diff,
                    salary_range=salary, market_demand=demand,
                    is_active=True
                )
                db.session.add(role)
            role_map[code] = role
        db.session.flush()
        print(f"Verified {len(roles_data)} career roles.")

        # 4. ROLE SKILL REQUIREMENTS MATRIX
        # (role_code, skill_code, required_level, score, importance, weight)
        requirements_matrix = [
            # Python Developer (CR-102) -> Exactly mirrors prompt example!
            ('CR-102', 'SK-PYT', 'Advanced', 3, 'Core', 5),
            ('CR-102', 'SK-SQL', 'Intermediate', 2, 'Core', 4),
            ('CR-102', 'SK-HTML', 'Beginner', 1, 'Supporting', 2),
            ('CR-102', 'SK-FLK', 'Intermediate', 2, 'Core', 4),
            ('CR-102', 'SK-API', 'Intermediate', 2, 'Core', 4),
            ('CR-102', 'SK-GIT', 'Intermediate', 2, 'Recommended', 3),
            ('CR-102', 'SK-PGS', 'Intermediate', 2, 'Recommended', 3),
            ('CR-102', 'SK-DOC', 'Beginner', 1, 'Optional', 2),

            # Web Developer (CR-101)
            ('CR-101', 'SK-HTML', 'Advanced', 3, 'Core', 5),
            ('CR-101', 'SK-CSS', 'Advanced', 3, 'Core', 5),
            ('CR-101', 'SK-JS', 'Intermediate', 2, 'Core', 4),
            ('CR-101', 'SK-GIT', 'Intermediate', 2, 'Recommended', 3),
            ('CR-101', 'SK-SQL', 'Beginner', 1, 'Supporting', 2),
            ('CR-101', 'SK-API', 'Intermediate', 2, 'Recommended', 3),

            # Data Analyst (CR-104)
            ('CR-104', 'SK-SQL', 'Advanced', 3, 'Core', 5),
            ('CR-104', 'SK-PYT', 'Intermediate', 2, 'Core', 4),
            ('CR-104', 'SK-DA', 'Advanced', 3, 'Core', 5),
            ('CR-104', 'SK-ML', 'Beginner', 1, 'Recommended', 3),
            ('CR-104', 'SK-GIT', 'Beginner', 1, 'Supporting', 2),

            # AI / ML Engineer (CR-106)
            ('CR-106', 'SK-PYT', 'Advanced', 3, 'Core', 5),
            ('CR-106', 'SK-ML', 'Advanced', 3, 'Core', 5),
            ('CR-106', 'SK-DA', 'Intermediate', 2, 'Core', 4),
            ('CR-106', 'SK-GEN', 'Intermediate', 2, 'Core', 4),
            ('CR-106', 'SK-DOC', 'Intermediate', 2, 'Recommended', 3),
            ('CR-106', 'SK-API', 'Intermediate', 2, 'Recommended', 3),

            # Cloud & DevOps (CR-107)
            ('CR-107', 'SK-LNX', 'Advanced', 3, 'Core', 5),
            ('CR-107', 'SK-DOC', 'Advanced', 3, 'Core', 5),
            ('CR-107', 'SK-K8S', 'Intermediate', 2, 'Core', 4),
            ('CR-107', 'SK-AWS', 'Intermediate', 2, 'Core', 4),
            ('CR-107', 'SK-GIT', 'Advanced', 3, 'Core', 4),
            ('CR-107', 'SK-PYT', 'Intermediate', 2, 'Recommended', 3)
        ]

        for r_code, s_code, req_level, req_score, imp, w in requirements_matrix:
            role = role_map.get(r_code)
            skill = skill_map.get(s_code)
            if role and skill:
                existing = RoleSkillRequirement.query.filter_by(career_role_id=role.id, skill_id=skill.id).first()
                if not existing:
                    req = RoleSkillRequirement(
                        career_role_id=role.id,
                        skill_id=skill.id,
                        required_level=req_level,
                        required_score=req_score,
                        importance=imp,
                        weight=w
                    )
                    db.session.add(req)
        db.session.flush()
        print("Verified role skill requirement matrices.")

        # 5. CURATED LEARNING RESOURCES (REAL OFFICIAL URLS)
        resources_data = [
            # Python
            ('SK-PYT', 'Python Official Tutorial', 'Documentation', 'Python Software Foundation', 'https://docs.python.org/3/tutorial/', '3-5 Hours', 'Beginner'),
            ('SK-PYT', 'Python for Beginners (freeCodeCamp)', 'Video', 'freeCodeCamp', 'https://www.youtube.com/watch?v=eWRfhZUzrAc', '6 Hours', 'Beginner'),
            ('SK-PYT', 'Core Python Programming Sandbox', 'Practice Website', 'W3Schools', 'https://www.w3schools.com/python/', '4 Hours', 'Beginner'),

            # Flask
            ('SK-FLK', 'Flask Official Quickstart & Documentation', 'Documentation', 'Pallets Project', 'https://flask.palletsprojects.com/en/stable/quickstart/', '4 Hours', 'Intermediate'),
            ('SK-FLK', 'Flask Mega-Tutorial by Miguel Grinberg', 'Tutorial', 'Miguel Grinberg Blog', 'https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world', '12 Hours', 'Intermediate'),

            # SQL & PostgreSQL
            ('SK-SQL', 'SQL Tutorial & Interactive Queries', 'Practice Website', 'SQLZoo', 'https://sqlzoo.net/wiki/SQL_Tutorial', '5 Hours', 'Beginner'),
            ('SK-PGS', 'PostgreSQL Official Documentation', 'Documentation', 'PostgreSQL Global Development Group', 'https://www.postgresql.org/docs/current/tutorial.html', '6 Hours', 'Intermediate'),

            # HTML & CSS
            ('SK-HTML', 'MDN HTML Developer Guide', 'Documentation', 'Mozilla MDN', 'https://developer.mozilla.org/en-US/docs/Learn/HTML', '4 Hours', 'Beginner'),
            ('SK-CSS', 'MDN CSS Layout & Flexbox Guide', 'Documentation', 'Mozilla MDN', 'https://developer.mozilla.org/en-US/docs/Learn/CSS', '5 Hours', 'Beginner'),

            # JavaScript & React
            ('SK-JS', 'Modern JavaScript Tutorial', 'Tutorial', 'JavaScript.info', 'https://javascript.info/', '10 Hours', 'Intermediate'),
            ('SK-REA', 'React Official Interactive Quick Start', 'Official Learning Platform', 'React Foundation', 'https://react.dev/learn', '6 Hours', 'Intermediate'),

            # Git & GitHub
            ('SK-GIT', 'Pro Git Official Book & Cheat Sheet', 'Documentation', 'Git SCM', 'https://git-scm.com/book/en/v2', '4 Hours', 'Beginner'),

            # Docker & DevOps
            ('SK-DOC', 'Docker Getting Started Guide', 'Documentation', 'Docker Docs', 'https://docs.docker.com/get-started/', '3 Hours', 'Intermediate'),
            ('SK-K8S', 'Kubernetes Basics Interactive Tutorial', 'Official Learning Platform', 'CNCF Kubernetes', 'https://kubernetes.io/docs/tutorials/kubernetes-basics/', '5 Hours', 'Advanced'),

            # APIs
            ('SK-API', 'RESTful API Design Best Practices', 'Documentation', 'Microsoft Learn', 'https://learn.microsoft.com/en-us/azure/architecture/best-practices/api-design', '3 Hours', 'Intermediate'),

            # AI & Data
            ('SK-DA', 'Pandas User Guide & Exercises', 'Documentation', 'PyData Pandas', 'https://pandas.pydata.org/docs/user_guide/index.html', '6 Hours', 'Intermediate'),
            ('SK-ML', 'Scikit-Learn Machine Learning in Python', 'Documentation', 'Scikit-Learn Developers', 'https://scikit-learn.org/stable/tutorial/index.html', '8 Hours', 'Intermediate'),
            ('SK-GEN', 'Prompt Engineering Guide for Generative AI', 'Documentation', 'DAIR.AI', 'https://www.promptingguide.ai/', '4 Hours', 'Intermediate')
        ]

        for s_code, title, r_type, provider, url, duration, diff in resources_data:
            skill = skill_map.get(s_code)
            if skill:
                existing = LearningResource.query.filter_by(title=title, skill_id=skill.id).first()
                if not existing:
                    res = LearningResource(
                        skill_id=skill.id,
                        title=title,
                        resource_type=r_type,
                        provider=provider,
                        url=url,
                        estimated_time=duration,
                        difficulty=diff,
                        is_active=True
                    )
                    db.session.add(res)
        db.session.flush()
        print(f"Verified {len(resources_data)} learning resources.")

        # 6. SAMPLE STUDENT (ALEX KUMAR)
        # Matches prompt example:
        # Python: Intermediate (Target Advanced -> Improvement Needed)
        # SQL: Beginner (Target Intermediate -> Improvement Needed)
        # HTML: Intermediate (Target Beginner -> Skill Available)
        # Flask: Not Assessed (Target Intermediate -> Missing Skill)
        # REST APIs: Not Assessed (Missing Skill)
        # Git: Intermediate (Skill Available)
        student = User.query.filter_by(email='alex.kumar@university.edu').first()
        if not student:
            student = User(
                email='alex.kumar@university.edu',
                full_name='Alex Kumar',
                role='student',
                is_active=True
            )
            student.set_password('studentpassword123')
            db.session.add(student)
            db.session.flush()

            profile = StudentProfile(
                user_id=student.id,
                phone='+91 98765 43210',
                institute='Apex Institute of Technology & Sciences, Pune',
                degree='Master of Computer Applications (MCA)',
                semester='Semester 4 (Final Year • Project Phase)',
                target_career_role_id=role_map['CR-102'].id,
                github_url='github.com/alexkumar-dev',
                linkedin_url='linkedin.com/in/alexkumar-mca',
                bio='Final-year MCA student specializing in Python backend architectures, microservices, and database systems.'
            )
            db.session.add(profile)
            db.session.flush()

            # Pre-assess student skills
            assessments = [
                ('SK-PYT', 'Intermediate', 2),
                ('SK-SQL', 'Beginner', 1),
                ('SK-HTML', 'Intermediate', 2),
                ('SK-CSS', 'Beginner', 1),
                ('SK-GIT', 'Intermediate', 2),
                ('SK-JS', 'Beginner', 1)
            ]
            for s_code, level, score in assessments:
                s = skill_map.get(s_code)
                if s:
                    db.session.add(StudentSkill(
                        user_id=student.id,
                        skill_id=s.id,
                        proficiency_level=level,
                        proficiency_score=score
                    ))
            db.session.flush()

            # Run initial gap analysis & roadmap for Alex Kumar
            analysis = calculate_skill_gap(student.id, role_map['CR-102'].id)
            generate_learning_roadmap(student.id, analysis.id)
            print("Created Sample Student Alex Kumar: alex.kumar@university.edu / studentpassword123")

        db.session.commit()
        print("Database seed completed successfully!")

if __name__ == '__main__':
    seed_database()
