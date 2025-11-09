from flask import Flask, render_template
from routes.tl_status import traffic_light_status_bp # blueprint

app = Flask(__name__)
app.register_blueprint(traffic_light_status_bp)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)