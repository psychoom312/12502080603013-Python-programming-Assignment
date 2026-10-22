import csv
import sys
import mysql.connector
from mysql.connector import Error

def run_analytics_engine(db_config, student_csv, registration_csv, target_course, spi_thresh):
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Student (
                student_id INT PRIMARY KEY,
                name VARCHAR(100),
                spi DECIMAL(4,2),
                INDEX idx_spi (spi)
            ) ENGINE=InnoDB;
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS CourseRegistration (
                registration_id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT,
                course_id VARCHAR(20),
                FOREIGN KEY (student_id) REFERENCES Student(student_id),
                INDEX idx_course_student (course_id, student_id)
            ) ENGINE=InnoDB;
        """)
        connection.commit()

        with open(student_csv, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            student_data = [row for row in reader if row]
            
        student_query = "INSERT IGNORE INTO Student (student_id, name, spi) VALUES (%s, %s, %s)"
        batch_size = 10000
        for i in range(0, len(student_data), batch_size):
            cursor.executemany(student_query, student_data[i:i+batch_size])
        connection.commit()

        with open(registration_csv, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            reg_data = [row for row in reader if row]
            
        reg_query = "INSERT INTO CourseRegistration (student_id, course_id) VALUES (%s, %s)"
        for i in range(0, len(reg_data), batch_size):
            cursor.executemany(reg_query, reg_data[i:i+batch_size])
        connection.commit()

        select_query = """
            SELECT s.student_id, s.name, s.spi, r.course_id
            FROM Student s
            JOIN CourseRegistration r ON s.student_id = r.student_id
            WHERE r.course_id = %s AND s.spi > %s
            ORDER BY s.spi DESC, s.student_id ASC
        """
        cursor.execute(select_query, (target_course, spi_thresh))
        results = cursor.fetchall()

        for row in results:
            print(f"{row[0]} {row[1]} {float(row[2])} {row[3]}")

    except Error as e:
        pass
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

if __name__ == "__main__":
    config = {
        'host': 'localhost',
        'database': 'university_db',
        'user': 'root',
        'password': 'password'
    }
    
    if len(sys.argv) > 2:
        c_id = sys.argv[1]
        s_threshold = float(sys.argv[2])
        run_analytics_engine(config, "student.csv", "registration.csv", c_id, s_threshold)
