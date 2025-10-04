from flask import Flask, jsonify, request, send_from_directory, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__, static_folder="../static", static_url_path="/")
CORS(app, supports_credentials=True)

# Secret key for sessions -- in production use ENV var
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "events.db")
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_PATH}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/static/login.html"

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    pw_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start = db.Column(db.String(32), nullable=True)
    end = db.Column(db.String(32), nullable=True)
    location = db.Column(db.String(200), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    contact = db.Column(db.String(200), nullable=True)
    notes = db.Column(db.Text, nullable=True)

class Attendee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=True)
    ticket_type = db.Column(db.String(100), nullable=True)

class ScheduleItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    start = db.Column(db.String(32), nullable=True)
    end = db.Column(db.String(32), nullable=True)
    speaker = db.Column(db.String(200), nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.before_first_request
def create_tables():
    db.create_all()

# Serve frontend
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

# Serve other static html
@app.route("/dashboard")
def dashboard_route():
    return send_from_directory(app.static_folder, "dashboard.html")

# Auth endpoints
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")
    if not username or not password:
        return jsonify({"error": "username and password required"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "username already exists"}), 400
    u = User(username=username, pw_hash=generate_password_hash(password))
    db.session.add(u); db.session.commit()
    return jsonify({"ok": True}), 201

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")
    u = User.query.filter_by(username=username).first()
    if not u or not u.check_password(password):
        return jsonify({"error": "invalid credentials"}), 401
    login_user(u)
    return jsonify({"ok": True, "username": u.username})

@app.route("/api/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"ok": True})

@app.route("/api/whoami", methods=["GET"])
def whoami():
    if current_user.is_authenticated:
        return jsonify({"username": current_user.username, "id": current_user.id})
    return jsonify({"username": None})

# API: Events
@app.route("/api/events", methods=["GET", "POST"])
def events():
    if request.method == "GET":
        q = request.args.get("q", "").lower()
        events_q = Event.query.order_by(Event.start.asc()).all()
        result = []
        for e in events_q:
            if q and q not in (e.title or "").lower() and q not in (e.location or "").lower():
                continue
            result.append({
                "id": e.id,
                "title": e.title,
                "description": e.description,
                "start": e.start,
                "end": e.end,
                "location": e.location,
                "created_by": e.created_by
            })
        return jsonify(result)
    else:
        # create requires login
        if not current_user.is_authenticated:
            return jsonify({"error": "authentication required"}), 401
        data = request.get_json() or {}
        e = Event(
            title = data.get("title","Untitled Event"),
            description = data.get("description"),
            start = data.get("start"),
            end = data.get("end"),
            location = data.get("location"),
            created_by = current_user.id
        )
        db.session.add(e); db.session.commit()
        return jsonify({"id": e.id}), 201

@app.route("/api/events/<int:event_id>", methods=["GET","PUT","DELETE"])
def event_detail(event_id):
    e = Event.query.get_or_404(event_id)
    if request.method == "GET":
        return jsonify({"id": e.id, "title": e.title, "description": e.description, "start": e.start, "end": e.end, "location": e.location, "created_by": e.created_by})
    if request.method == "PUT":
        # only creator can edit
        if not current_user.is_authenticated or current_user.id != (e.created_by or 0):
            return jsonify({"error": "not allowed"}), 403
        data = request.get_json() or {}
        e.title = data.get("title", e.title)
        e.description = data.get("description", e.description)
        e.start = data.get("start", e.start)
        e.end = data.get("end", e.end)
        e.location = data.get("location", e.location)
        db.session.commit()
        return jsonify({"ok": True})
    if request.method == "DELETE":
        if not current_user.is_authenticated or current_user.id != (e.created_by or 0):
            return jsonify({"error": "not allowed"}), 403
        db.session.delete(e); db.session.commit()
        return jsonify({"ok": True})

# API: Vendors (public create allowed for simplicity)
@app.route("/api/vendors", methods=["GET","POST"])
def vendors():
    if request.method == "GET":
        vlist = Vendor.query.all()
        return jsonify([{"id":v.id,"name":v.name,"contact":v.contact,"notes":v.notes} for v in vlist])
    data = request.get_json() or {}
    v = Vendor(name=data.get("name","Unnamed Vendor"), contact=data.get("contact"), notes=data.get("notes"))
    db.session.add(v); db.session.commit()
    return jsonify({"id": v.id}), 201

# API: Attendees
@app.route("/api/attendees", methods=["GET","POST"])
def attendees():
    if request.method == "GET":
        alist = Attendee.query.all()
        return jsonify([{"id":a.id,"name":a.name,"email":a.email,"ticket_type":a.ticket_type} for a in alist])
    data = request.get_json() or {}
    a = Attendee(name=data.get("name","Anonymous"), email=data.get("email"), ticket_type=data.get("ticket_type"))
    db.session.add(a); db.session.commit()
    return jsonify({"id": a.id}), 201

# API: Schedule
@app.route("/api/schedule", methods=["GET","POST"])
def schedule():
    if request.method == "GET":
        items = ScheduleItem.query.all()
        return jsonify([{"id":s.id,"event_id":s.event_id,"title":s.title,"start":s.start,"end":s.end,"speaker":s.speaker} for s in items])
    data = request.get_json() or {}
    s = ScheduleItem(event_id=data.get("event_id"), title=data.get("title","Untitled"), start=data.get("start"), end=data.get("end"), speaker=data.get("speaker"))
    db.session.add(s); db.session.commit()
    return jsonify({"id": s.id}), 201

# Lightweight coordination endpoint: assign vendor to event (simple note)
@app.route("/api/events/<int:event_id>/assign_vendor", methods=["POST"])
@login_required
def assign_vendor(event_id):
    data = request.get_json() or {}
    vendor_id = data.get("vendor_id")
    vendor = Vendor.query.get(vendor_id)
    ev = Event.query.get(event_id)
    if not vendor or not ev:
        return jsonify({"error":"invalid vendor or event id"}), 400
    si = ScheduleItem(event_id=ev.id, title=f"Vendor: {vendor.name}", start=None, end=None, speaker=vendor.contact or "")
    db.session.add(si); db.session.commit()
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
