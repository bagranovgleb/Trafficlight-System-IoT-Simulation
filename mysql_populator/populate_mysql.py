import time
import mysql.connector
from mysql.connector import Error
from config import MYSQL_CONFIG

def wait_for_mysql_connection():
    for attempt in range(15):
        try:
            conn = mysql.connector.connect(**MYSQL_CONFIG)
            if conn.is_connected():
                print(f"[OK] Connected to MySQL on attempt {attempt + 1}")
                return conn
        except Error as e:
            print(f"[WAIT] MySQL not ready: {e}, retrying (attempt {attempt + 1}/15)...")
        time.sleep(5)
    raise Exception("MySQL not available after multiple attempts.")

print("=== [BOOT] mysql_populator.py started ===")

try:
    mysql_conn = wait_for_mysql_connection()
    cursor = mysql_conn.cursor()

    print("[INFO] Dropping and creating database 'smarttrafficlight'...")
    cursor.execute("DROP DATABASE IF EXISTS smarttrafficlight")
    cursor.execute("CREATE DATABASE smarttrafficlight")
    cursor.execute("USE smarttrafficlight")

    print("[INFO] Creating table 'trafficlights'...")
    create_table_query = """
    CREATE TABLE trafficlights (
        tl_id INT AUTO_INCREMENT PRIMARY KEY,
        tl_name VARCHAR(100) NOT NULL,
        tl_intersection VARCHAR(100) NOT NULL,
        tl_productiondate DATE NOT NULL
    )ENGINE=InnoDB;
    """
    cursor.execute(create_table_query)
    print("[OK] Table 'trafficlights' created.")

    print("[INFO] Inserting initial data into 'trafficlights'...")
    insert_data_query = """
    INSERT INTO trafficlights (tl_name, tl_intersection, tl_productiondate) VALUES
    ('Apple-Blueberry',           'Apple St & Blueberry St',     '2008-11-01'),
    ('Apple-Potato',              'Apple St & Potato St',        '2017-10-01'),
    ('Apple-Cherry',              'Apple St & Cherry St',        '2019-05-01'),
    ('Apple-Strawberry',          'Apple St & Strawberry St',    '2019-05-01'),
    ('Apple-Lemon',               'Apple St & Lemon St',         '2019-05-01'),
    ('Pineapple-Cherry',          'Pineapple St & Cherry St',    '2020-03-01'),
    ('Pineapple-Strawberry',      'Pineapple St & Strawberry St', '2020-03-01'),
    ('Pineapple-Lemon',           'Pineapple St & Lemon St',     '2020-03-01'),
    ('Pear-Potato',               'Pear St & Potato St',         '2020-03-01'),
    ('Pear-Cherry',               'Pear St & Cherry St',         '2022-07-01'),
    ('Pear-Strawberry',           'Pear St & Strawberry St',     '2022-07-01');
    """
    cursor.execute(insert_data_query)
    mysql_conn.commit()
    print("[OK] Initial data inserted.")

except Exception as e:
    print(f"[FATAL] Error during MySQL population: {e}")
    exit(1)
finally:
    if 'mysql_conn' in locals() and mysql_conn.is_connected():
        cursor.close()
        mysql_conn.close()
        print("[INFO] MySQL connection closed.")

print("=== [DONE] mysql_populator.py finished ===")