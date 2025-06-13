from app import create_app, socketio
import os

app = create_app()

if __name__ == '__main__':
    socketio.run(app, port=int(os.environ.get('PORT', 5000)), debug=True)
