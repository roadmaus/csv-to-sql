import sqlite3
import pandas as pd
import argparse
import re
from PyInquirer import prompt

import os

def create_connection(db_file):
    """Create a database connection to a SQLite database"""
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return None

def create_table(conn, create_table_sql):
    """Create a table from the create_table_sql statement"""
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print(e)

def sanitize_table_name(name):
    """ Sanitize the table name to ensure it adheres to SQL naming conventions """
    name = re.sub(r'\W+', '_', name)  
    return name

def check_date_exists(conn, table_name, date):
    """Check if the date already exists in the table and return the latest stop time if it does"""
    query = f"SELECT Letzte_Stoppzeit FROM {table_name} WHERE Datum = ?"
    cur = conn.cursor()
    cur.execute(query, (date,))
    result = cur.fetchone()
    return result[0] if result else None

def create_and_populate_tables(csv_data, database_path, progress_callback):
    conn = create_connection(database_path)

    if conn:
        with conn:
            for fahrzeugname in csv_data['Fahrzeugname'].unique():
                table_name = sanitize_table_name(fahrzeugname)
                progress_callback(f"Creating table: {table_name}")

                create_table_sql = f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    Datum TEXT,
                    Erster_Startort TEXT,
                    Erste_Startzeit TEXT,
                    Letzter_Stoppstandort TEXT,
                    Letzte_Stoppzeit TEXT
                );
                """
                create_table(conn, create_table_sql)

                fahrzeug_data = csv_data[csv_data['Fahrzeugname'] == fahrzeugname]
                for date in fahrzeug_data['Datum'].unique():
                    daily_data = fahrzeug_data[fahrzeug_data['Datum'] == date]
                    first_start = daily_data.iloc[0]
                    last_stop = daily_data.iloc[-1]

                    existing_stoppzeit = check_date_exists(conn, table_name, date)
                    if existing_stoppzeit:
                        new_stoppzeit = last_stop['Ankunftszeit']
                        if new_stoppzeit > existing_stoppzeit:
                            update_sql = f"""UPDATE {table_name} SET 
                                                Erster_Startort = ?, 
                                                Erste_Startzeit = ?, 
                                                Letzter_Stoppstandort = ?, 
                                                Letzte_Stoppzeit = ?
                                            WHERE Datum = ?;"""
                            conn.execute(update_sql, (first_start['Startstandort'], first_start['Startzeit'], 
                                                      last_stop['Stoppstandort'], new_stoppzeit, date))
                            progress_callback(f"Updated entry for {date} in table {table_name}")
                        else:
                            progress_callback(f"Skipped earlier or same entry for {date} in table {table_name}")
                    else:
                        insert_sql = f"""INSERT INTO {table_name} (Datum, Erster_Startort, Erste_Startzeit, Letzter_Stoppstandort, Letzte_Stoppzeit) 
                                        VALUES (?, ?, ?, ?, ?);"""
                        conn.execute(insert_sql, (date, first_start['Startstandort'], first_start['Startzeit'], 
                                                  last_stop['Stoppstandort'], last_stop['Ankunftszeit']))
                        progress_callback(f"Inserted new entry for {date} in table {table_name}")

        print("Data successfully imported into SQLite database.")
    else:
        print("Failed to create database connection.")

def create_xlsx_file(database_path, xlsx_path, progress_callback):
    conn = create_connection(database_path)
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cur.fetchall()

        with pd.ExcelWriter(xlsx_path, engine='xlsxwriter') as writer:
            for table in tables:
                fahrzeugname = table[0]
                query = f"SELECT * FROM {fahrzeugname}"
                df = pd.read_sql_query(query, conn)

                df.to_excel(writer, sheet_name=fahrzeugname, index=False)

                worksheet = writer.sheets[fahrzeugname]
                worksheet.set_column('A:A', 10)  # Datum
                worksheet.set_column('B:B', 70)  # Erster_Startort
                worksheet.set_column('C:C', 13)  # Erste_Startzeit
                worksheet.set_column('D:D', 70)  # Letzter_Stoppstandort
                worksheet.set_column('E:E', 13)  # Letzte_Stoppzeit
                progress_callback(f"Mirrored data to sheet: {fahrzeugname}")

    else:
        print("Failed to create database connection.")


def get_user_inputs():
    questions = [
        {
            'type': 'input',
            'name': 'csv_file',
            'message': 'Enter the path to your CSV file:',
        },
        {
            'type': 'input',
            'name': 'db_file',
            'message': 'Enter the path to your SQLite database file:',
        },
        {
            'type': 'input',
            'name': 'xlsx_file',
            'message': 'Enter the name for your XLSX file (including .xlsx):',
        }
    ]
    answers = prompt(questions)
    return answers['csv_file'], answers['db_file'], answers['xlsx_file']


def main_process(csv_file_path, db_file_path, xlsx_file_path, progress_callback):
    # Call the callback function with a progress update
    progress_callback("<font color='#ff843d'>Starting process...</font>")

    csv_data = pd.read_csv(csv_file_path, delimiter=';')
    progress_callback("<font color='#d5ff3d'>CSV data loaded  ✓</font>")

    create_and_populate_tables(csv_data, db_file_path, progress_callback)
    progress_callback("<font color='#d5ff3d'>Tables created and populated  ✓</font>")

    create_xlsx_file(db_file_path, xlsx_file_path, progress_callback)
    progress_callback("<font color='#d5ff3d'>XLSX file created  ✓</font>")

    progress_callback("<font color='#64ff3d'>Process completed successfully  ✓</font>")

