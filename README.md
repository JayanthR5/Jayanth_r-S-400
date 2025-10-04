# Event Coordination Chaos

A simplified event management system.

## Setup
1️⃣ Clone or Extract the Project
cd EventCoordinationChaos

If cloning from GitHub:
git clone https://github.com/<your-username>/EventCoordinationChaos.git
cd EventCoordinationChaos

2️⃣ Create & Activate a Virtual Environment
python -m venv venv
venv\Scripts\activate

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Run the Application
python backend/app.py


By default, the app runs on:

http://127.0.0.1:5000/

Run Tests

To verify that everything works:

pytest -v

=============================================================================
# Run with Docker
1️⃣ Build Docker Image
docker build -t event-coordination-chaos -f deploy/Dockerfile .

2️⃣ Run Container
docker run -p 5000:5000 event-coordination-chaos


App will be available at:

http://localhost:5000


You can then open static/index.html and use the app.
==============================================================================


 
 # Environment Variables (Optional)

You can modify the following in backend/app.py:

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SECRET_KEY'] = 'supersecretkey'


If deploying, consider setting environment variables:

export SECRET_KEY="your_strong_secret"
export DATABASE_URL="sqlite:///events.db"
=================================================================================

# Troubleshooting
Issue                          Solution
flask_sqlalchemy not found	-  Run pip install flask_sqlalchemy
CORS errors in browser	    -  Make sure Flask app runs with CORS(app, supports_credentials=True)
Database not updating	    - Delete events.db and rerun app to recreate tables
Port already in use	        - Run app on another port: flask run -p 5001
===================================================================================


# simple project structure
EventCoordinationChaos/
│
├── backend/
│   └── app.py                 # Flask backend with authentication & event APIs
│
├── static/
│   ├── main.html             # Frontend UI
│   ├── app.js                 # JavaScript API calls
│                
│
├── tests/
│   └── test_app.py            # Pytest unit tests
│
├── deploy/
│   └── Dockerfile             # Container configuration
│
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
└── .gitignore                 # (optional)


======================================================================================
# Author

Jayanth R (AIML)
3rd Year | Event Coordination Chaos Project
📧 Open for collaboration or improvements!


