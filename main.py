import sqlite3
import pandas as pd
import re
from PyInquirer import prompt

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
    """Sanitize the table name to ensure it adheres to SQL naming conventions"""
    name = re.sub(r'\W+', '_', name)  
    return name

def check_date_exists(conn, table_name, date):
    """Check if the date already exists in the table and return the existing trip times if it does"""
    query = f"SELECT ErsterTripVonBis, LetzterTripVonBis FROM {table_name} WHERE Datum = ?"
    cur = conn.cursor()
    cur.execute(query, (date,))
    result = cur.fetchone()
    return result if result else None

def create_and_populate_tables(csv_data, database_path, progress_callback):
    conn = create_connection(database_path)

    if conn:
        with conn:
            for fahrzeugname in csv_data['Fahrzeugname'].unique():
                table_name = sanitize_table_name(fahrzeugname)
                progress_callback(f"Creating table: {table_name}")

                # New SQL statement for table creation
                create_table_sql = f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    Datum DATE,
                    ErsterTripVonBis TEXT,
                    ErsterTripOrte TEXT,
                    LetzterTripVonBis TEXT,
                    LetzterTripOrte TEXT
                );
                """
                create_table(conn, create_table_sql)

                fahrzeug_data = csv_data[csv_data['Fahrzeugname'] == fahrzeugname]
                for date in fahrzeug_data['Datum'].unique():
                    daily_data = fahrzeug_data[fahrzeug_data['Datum'] == date]

                    if len(daily_data) == 0:
                        continue  # Skip days with no trips

                    # Sorting data to find the first and last trips
                    daily_data_sorted_by_start = daily_data.sort_values('Startzeit')
                    daily_data_sorted_by_end = daily_data.sort_values('Ankunftszeit')

                    first_trip = daily_data_sorted_by_start.iloc[0]
                    last_trip = daily_data_sorted_by_end.iloc[-1]

                    # Preparing data for insertion
                    erster_trip_von_bis = f"{first_trip['Startzeit']} - {first_trip['Ankunftszeit']}"
                    erster_trip_orte = f"{first_trip['Startstandort']} - {first_trip['Stoppstandort']}"
                    letzter_trip_von_bis = f"{last_trip['Startzeit']} - {last_trip['Ankunftszeit']}"
                    letzter_trip_orte = f"{last_trip['Startstandort']} - {last_trip['Stoppstandort']}"

                    existing_entry = check_date_exists(conn, table_name, date)
                    if existing_entry:
                        existing_erster_trip_von_bis, existing_letzter_trip_von_bis = existing_entry
                        if (erster_trip_von_bis > existing_erster_trip_von_bis or letzter_trip_von_bis > existing_letzter_trip_von_bis):
                            # Update the existing entry
                            update_sql = f"""UPDATE {table_name} SET 
                                                ErsterTripVonBis = ?, 
                                                ErsterTripOrte = ?, 
                                                LetzterTripVonBis = ?, 
                                                LetzterTripOrte = ?
                                            WHERE Datum = ?;"""
                            conn.execute(update_sql, (erster_trip_von_bis, erster_trip_orte, 
                                                      letzter_trip_von_bis, letzter_trip_orte, date))
                            progress_callback(f"Updated entry for {date} in table {table_name}")
                        else:
                            # Skip the entry as it's not newer
                            progress_callback(f"Skipped entry for {date} in table {table_name} as it's not newer")
                    else:
                        # Insert a new entry
                        insert_sql = f"""INSERT INTO {table_name} (Datum, ErsterTripVonBis, ErsterTripOrte, LetzterTripVonBis, LetzterTripOrte) 
                                        VALUES (?, ?, ?, ?, ?);"""
                        conn.execute(insert_sql, (date, erster_trip_von_bis, erster_trip_orte, 
                                                  letzter_trip_von_bis, letzter_trip_orte))
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
                # Adjust column widths as needed for the new structure
                worksheet.set_column('A:A', 12)  # Datum
                worksheet.set_column('B:B', 25)  # ErsterTripVonBis
                worksheet.set_column('C:C', 100)  # ErsterTripOrte
                worksheet.set_column('D:D', 25)  # LetzterTripVonBis
                worksheet.set_column('E:E', 100)  # LetzterTripOrte
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

