import streamlit as st
import pyodbc
import pandas as pd

# ==========================
# PAGE SETTINGS
# ==========================


st.set_page_config(
    page_title="Student Performance Analytics",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Student Performance Analytics Dashboard")

# ==========================
# DATABASE CONNECTION
# ==========================

def get_connection():
    return pyodbc.connect(
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=localhost\\SQLEXPRESS;"
        "Database=StudentAnalytics;"
        "Trusted_Connection=yes;"
    )

# ==========================
# SIDEBAR
# ==========================

st.sidebar.title("📌 Navigation")

option = st.sidebar.radio(
    "Select Report",
    [

        "🏠 Home",
        "🏆 Topper",
        "🥇 Top 5 Students",
        "📊 Branch Performance",
        "📚 Subject Performance",
        "🔍 Search Student",
        "🏅 Subject Toppers",
        "👤 Student Report Card",
    ]
)
# ==========================
# HOME
# ==========================

if option == "🏠 Home":

    conn = get_connection()

    total_students = pd.read_sql(
        "SELECT COUNT(*) AS TotalStudents FROM Student",
        conn
    ).iloc[0, 0]

    total_subjects = pd.read_sql(
        "SELECT COUNT(DISTINCT subject) AS TotalSubjects FROM Marks",
        conn
    ).iloc[0, 0]

    avg_marks = pd.read_sql(
        "SELECT AVG(marks) AS AvgMarks FROM Marks",
        conn
    ).iloc[0, 0]

    highest_percentage = pd.read_sql(
    """
    SELECT MAX(Percentage) AS HighestPercentage
    FROM (
        SELECT AVG(marks) AS Percentage
        FROM Marks
        GROUP BY student_id
    ) t
    """,
    conn
    ).iloc[0, 0]

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    col1.metric("👨‍🎓 Total Students", total_students)
    col2.metric("📚 Total Subjects", total_subjects)
    col3.metric("📊 Average Marks", round(avg_marks, 2))
    col4.metric("🏆 Highest %", round(highest_percentage, 2))



    conn.close()

# ==========================
# TOPPER
# ==========================

elif option == "🏆 Topper":

    conn = get_connection()

    query = """
    SELECT TOP 1
        s.student_id,
        s.name,
        s.branch,
        AVG(m.marks) AS Percentage
    FROM Student s
    JOIN Marks m
        ON s.student_id = m.student_id
    GROUP BY s.student_id, s.name, s.branch
    ORDER BY Percentage DESC
    """

    df = pd.read_sql(query, conn)

    st.subheader("🏆 Topper")
    st.dataframe(df, width="stretch")

    conn.close()
   # ==========================
# TOP 5 STUDENTS
# ==========================

elif option == "🥇 Top 5 Students":

    conn = get_connection()

    query = """
    SELECT TOP 5
        s.student_id,
        s.name,
        s.branch,
        AVG(m.marks) AS Percentage
    FROM Student s
    JOIN Marks m
        ON s.student_id = m.student_id
    GROUP BY s.student_id, s.name, s.branch
    ORDER BY Percentage DESC
    """

    df = pd.read_sql(query, conn)

    st.subheader("🥇 Top 5 Students")
    st.dataframe(df, width="stretch")

    conn.close()

    # ==========================
# BRANCH PERFORMANCE
# ==========================

elif option == "📊 Branch Performance":

    conn = get_connection()

    query = """
    SELECT
        s.branch,
        AVG(m.marks) AS AverageMarks
    FROM Student s
    JOIN Marks m
        ON s.student_id = m.student_id
    GROUP BY s.branch
    ORDER BY AverageMarks DESC
    """

    df = pd.read_sql(query, conn)

    st.subheader("📊 Branch Performance")

    st.bar_chart(df.set_index("branch"))
    st.dataframe(df, width="stretch")

    conn.close()

    # ==========================
# SUBJECT PERFORMANCE
# ==========================

elif option == "📚 Subject Performance":

    conn = get_connection()

    query = """
    SELECT
        subject,
        AVG(marks) AS AverageMarks
    FROM Marks
    GROUP BY subject
    ORDER BY AverageMarks DESC
    """

    df = pd.read_sql(query, conn)

    st.subheader("📚 Subject Performance")

    st.bar_chart(df.set_index("subject"))
    st.dataframe(df, width="stretch")

    conn.close()

    # ==========================
# SUBJECT TOPPERS
# ==========================

elif option == "🏅 Subject Toppers":

    conn = get_connection()

    query = """
    SELECT
    m.subject,
    s.name,
    m.marks
    FROM Marks m
    JOIN Student s
    ON m.student_id = s.student_id
    WHERE m.marks = (
    SELECT MAX(m2.marks)
    FROM Marks m2
    WHERE m2.subject = m.subject)
    ORDER BY m.subject"""

    df = pd.read_sql(query, conn)

    st.subheader("🏅 Subject Toppers")

    st.dataframe(df, width="stretch")

    conn.close()

    # ==========================
# STUDENT REPORT CARD
# ==========================

elif option == "👤 Student Report Card":

    conn = get_connection()

    students = pd.read_sql(
        "SELECT student_id, name FROM Student",
        conn
    )

    student_name = st.selectbox(
        "Select Student",
        students["name"]
    )

    student_id = students[
        students["name"] == student_name
    ]["student_id"].iloc[0]

    query = f"""
    SELECT
        subject,
        marks
    FROM Marks
    WHERE student_id = {student_id}
    """

    df = pd.read_sql(query, conn)

    st.subheader(f"📄 Report Card - {student_name}")

    st.bar_chart(df.set_index("subject"))

    st.dataframe(df, width="stretch")

    conn.close()

    # ==========================
# SEARCH STUDENT
# ==========================

elif option == "🔍 Search Student":

    conn = get_connection()

    student_id = st.number_input(
        "Enter Student ID",
        min_value=1,
        step=1
    )

    if st.button("Search"):

        query = """
        SELECT
            s.student_id,
            s.name,
            s.branch,
            s.semester,
            AVG(m.marks) AS Percentage
        FROM Student s
        JOIN Marks m
            ON s.student_id = m.student_id
        WHERE s.student_id = ?
        GROUP BY
            s.student_id,
            s.name,
            s.branch,
            s.semester
        """

        df = pd.read_sql(
            query,
            conn,
            params=[student_id]
        )

        if len(df) > 0:

            st.subheader("🎓 Student Details")

            st.dataframe(
                df,
                width="stretch"
            )

            marks_query = """
            SELECT
                subject,
                marks
            FROM Marks
            WHERE student_id = ?
            """

            marks_df = pd.read_sql(
                marks_query,
                conn,
                params=[student_id]
            )

            st.subheader("📚 Subject Marks")

            st.bar_chart(
                marks_df.set_index("subject")
            )

            st.dataframe(
                marks_df,
                width="stretch"
            )

        else:

            st.error("❌ Student Not Found")

    conn.close()