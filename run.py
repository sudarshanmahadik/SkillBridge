import os
from app import create_app
from config import config_by_name

env = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_by_name.get(env, config_by_name['default']))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f" * Starting SkillBridge Application on http://127.0.0.1:{port}")
    app.run(host='127.0.0.1', port=port, debug=True)
