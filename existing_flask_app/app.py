from flask import Flask, render_template, request, Response, redirect, session
import sqlite3
import joblib


app = Flask(__name__)

app.secret_key = "healthcare_secret_key_2026"
model = joblib.load("ml/healthcare_model.pkl")


def classify_query(query):

    prediction = model.predict([query])[0]

    probabilities = model.predict_proba([query])[0]

    classes = model.classes_

    prediction_details = list(zip(classes, probabilities))

    prediction_details = sorted(
        prediction_details,
        key=lambda x: x[1],
        reverse=True
    )

    confidence = round(prediction_details[0][1] * 100)

    category_details = {

        "COBRA": (
            "High",
            "Critical",
            "COBRA Administration",
            "Verify participant eligibility and continuation coverage records."
        ),

        "Dependent Management": (
            "Medium",
            "Medium",
            "Benefits Administration",
            "Verify dependent enrollment and eligibility information."
        ),

        "Carrier Issue": (
            "High",
            "High",
            "Carrier Relations",
            "Verify carrier file transmission and enrollment records."
        ),

        "Claims Support": (
            "Low",
            "Low",
            "Claims Team",
            "Review claim details and carrier adjudication records."
        ),

        "Billing": (
            "Medium",
            "Medium",
            "Billing Operations",
            "Review premium calculation and billing records."
        ),

        "Life Event": (
            "Medium",
            "Medium",
            "Benefits Administration",
            "Review life event documentation and eligibility updates."
        ),

        "Enrollment": (
            "High",
            "High",
            "Eligibility Operations",
            "Review enrollment records and effective dates."
        )
    }

    priority, severity, team, recommendation = category_details.get(
        prediction,
        (
            "Medium",
            "Medium",
            "Benefits Team",
            "Review submitted healthcare benefits query."
        )
    )

    # Explainable AI - detected healthcare terms
    detected_terms = []

    important_words = [
        "cobra",
        "claim",
        "carrier",
        "premium",
        "invoice",
        "dependent",
        "spouse",
        "child",
        "coverage",
        "enrollment",
        "marriage",
        "birth",
        "billing",
        "reimbursement",
        "insurance"
    ]

    query_lower = query.lower()

    for word in important_words:
        if word in query_lower:
            detected_terms.append(word)

    return (
        prediction,
        priority,
        severity,
        team,
        recommendation,
        confidence,
        detected_terms,
        prediction_details[:3]
    )

@app.route('/', methods=['GET', 'POST'])
def home():

    # ===============================
    # Dashboard Statistics
    # ===============================
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM queries")
    total_queries = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM queries WHERE category='COBRA'")
    cobra_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM queries WHERE category='Carrier Issue'")
    carrier_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM queries WHERE category='Claims Support'")
    claims_count = cursor.fetchone()[0]

    conn.close()

    # ===============================
    # Process Form Submission
    # ===============================
    if request.method == 'POST':

        username = request.form['username'].strip()
        query = request.form['query'].strip()

        # Validation
        if len(username) < 3:

            return render_template(
                'error.html',
                message="Employee name must contain at least 3 characters."
            )

        if len(query) < 10:

            return render_template(
                'error.html',
                message="Please enter a more detailed healthcare benefits query."
            )

        # AI Prediction
        category, priority, severity, team, recommendation, confidence, detected_terms, predictions = classify_query(query)

        # Save to Database
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute(
            '''
            INSERT INTO queries
            (
                user_name,
                query_text,
                category,
                priority,
                assigned_team,
                recommendation,
                confidence_score
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                username,
                query,
                category,
                priority,
                team,
                recommendation,
                confidence
            )
        )

        conn.commit()
        conn.close()

        # Show AI Result
        return render_template(
            'result.html',
            username=username,
            category=category,
            priority=priority,
            severity=severity,
            team=team,
            recommendation=recommendation,
            confidence=confidence,
            detected_terms=detected_terms,
            predictions=predictions
        )

    # ===============================
    # First Page Load (GET Request)
    # ===============================
    return render_template(
        'index.html',
        total_queries=total_queries,
        cobra_count=cobra_count,
        carrier_count=carrier_count,
        claims_count=claims_count
    )

@app.route('/admin')
def admin():

    if not session.get('logged_in'):

        return redirect('/login')

    search = request.args.get('search', '')

    category_filter = request.args.get('category', '')

    conn = sqlite3.connect('database.db')

    cursor = conn.cursor()

    query = '''
    SELECT *
    FROM queries
    WHERE 1=1
    '''

    params = []

    if search:

        query += '''
        AND user_name LIKE ?
        '''

        params.append(f"%{search}%")

    if category_filter:

        query += '''
        AND category = ?
        '''

        params.append(category_filter)

    query += '''
    ORDER BY query_id DESC
    '''

    cursor.execute(query, params)

    rows = cursor.fetchall()

    # Dashboard Statistics

    cursor.execute(
        '''
        SELECT COUNT(*) FROM queries
        '''
    )
    total_queries = cursor.fetchone()[0]

    cursor.execute(
        '''
        SELECT COUNT(*)
        FROM queries
        WHERE priority='High'
        '''
    )
    high_priority = cursor.fetchone()[0]

    cursor.execute(
        '''
        SELECT COUNT(*)
        FROM queries
        WHERE priority='Medium'
        '''
    )
    medium_priority = cursor.fetchone()[0]

    cursor.execute(
        '''
        SELECT COUNT(*)
        FROM queries
        WHERE priority='Low'
        '''
    )
    low_priority = cursor.fetchone()[0]

    # Category Analytics

    cursor.execute(
        '''
        SELECT COUNT(*)
        FROM queries
        WHERE category='COBRA'
        '''
    )
    cobra_count = cursor.fetchone()[0]

    cursor.execute(
        '''
        SELECT COUNT(*)
        FROM queries
        WHERE category='Carrier Issue'
        '''
    )
    carrier_count = cursor.fetchone()[0]

    cursor.execute(
        '''
        SELECT COUNT(*)
        FROM queries
        WHERE category='Claims Support'
        '''
    )
    claims_count = cursor.fetchone()[0]

    cursor.execute(
        '''
        SELECT COUNT(*)
        FROM queries
        WHERE category='Billing'
        '''
    )
    billing_count = cursor.fetchone()[0]

    cursor.execute(
        '''
        SELECT COUNT(*)
        FROM queries
        WHERE category='Dependent Management'
        '''
    )
    dependent_count = cursor.fetchone()[0]

    conn.close()

    return render_template(
        'admin.html',
        rows=rows,
        total_queries=total_queries,
        high_priority=high_priority,
        medium_priority=medium_priority,
        low_priority=low_priority,
        cobra_count=cobra_count,
        carrier_count=carrier_count,
        claims_count=claims_count,
        billing_count=billing_count,
        dependent_count=dependent_count
    )
@app.route('/export')
def export():

    conn = sqlite3.connect('database.db')

    cursor = conn.cursor()

    cursor.execute(
        '''
        SELECT *
        FROM queries
        '''
    )

    rows = cursor.fetchall()

    conn.close()

    csv_data = "ID,User,Query,Category,Priority,Team,Recommendation,Confidence,Date\n"

    for row in rows:

        csv_data += (
            f"{row[0]},"
            f"{row[1]},"
            f"\"{row[2]}\","
            f"{row[3]},"
            f"{row[4]},"
            f"{row[5]},"
            f"\"{row[6]}\","
            f"{row[7]},"
            f"{row[8]}\n"
        )

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=Healthcare_Query_Report.csv"
        }
    )


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "admin123":

            session['logged_in'] = True
            session['username'] = username

            return redirect('/admin')

        else:

            return render_template(
    'login.html',
    error="Invalid Username or Password"
    )

    return render_template(
    'login.html',
    error=None
)
@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')
if __name__ == '__main__':
    app.run(debug=True)