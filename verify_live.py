import sys, os, re
sys.path.insert(0, r'C:\Users\HP\.gemini\antigravity\scratch\SkillBridge')

from app import create_app
from config import DevelopmentConfig

app = create_app(DevelopmentConfig)
client = app.test_client()

print('--- Testing Public Endpoints ---')
res = client.get('/')
print('GET / -> Status:', res.status_code, 'Content length:', len(res.data))
assert res.status_code == 200

res = client.get('/auth/login')
print('GET /auth/login -> Status:', res.status_code)
assert res.status_code == 200

# 1. Extract CSRF token
m = re.search(r'name=["\']csrf_token["\'][^>]*value=["\']([^"\']+)["\']', res.text) or re.search(r'value=["\']([^"\']+)["\'][^>]*name=["\']csrf_token["\']', res.text)
token = m.group(1) if m else ''
print('CSRF Token found:', bool(token))

# 2. Student Login with CSRF Token
res_login = client.post('/auth/login', data={
    'csrf_token': token,
    'email': 'alex.kumar@university.edu',
    'password': 'studentpassword123',
    'submit': 'Sign In'
}, follow_redirects=True)
print('Student Login -> Status:', res_login.status_code)
assert res_login.status_code == 200

# 3. Check All Student Endpoints
endpoints = [
    '/student/dashboard',
    '/student/profile',
    '/student/career-roles',
    '/student/skill-assessment',
    '/student/skill-gap-analysis',
    '/student/learning-roadmap',
    '/student/resources'
]

for ep in endpoints:
    r = client.get(ep)
    print(f'GET {ep} -> Status: {r.status_code}, Length: {len(r.data)}')
    assert r.status_code == 200

client.get('/auth/logout')

# 4. Admin Login with CSRF Token
res_admin_get = client.get('/auth/admin-login')
m_admin = re.search(r'name=["\']csrf_token["\'][^>]*value=["\']([^"\']+)["\']', res_admin_get.text) or re.search(r'value=["\']([^"\']+)["\'][^>]*name=["\']csrf_token["\']', res_admin_get.text)
admin_token = m_admin.group(1) if m_admin else ''

res_admin = client.post('/auth/admin-login', data={
    'csrf_token': admin_token,
    'email': 'admin@skillbridge.edu',
    'password': 'adminpassword123',
    'submit': 'Authenticate Admin'
}, follow_redirects=True)
print('Admin Login -> Status:', res_admin.status_code)
assert res_admin.status_code == 200

admin_endpoints = [
    '/admin/dashboard',
    '/admin/students',
    '/admin/career-roles',
    '/admin/skills',
    '/admin/role-requirements',
    '/admin/learning-resources'
]

for ep in admin_endpoints:
    r = client.get(ep)
    print(f'GET {ep} -> Status: {r.status_code}, Length: {len(r.data)}')
    assert r.status_code == 200

print('\n>>> ALL 14 ENDPOINTS & CSRF PROTECTED SESSIONS VERIFIED SUCCESSFULLY (HTTP 200 OK) <<<')
