import sqlite3
import string

# -- CONSTANTS -- #
DB_PATH = 'db/database.db'


def init_db():

    '''
    Run this to create the database for the bot.
    Should be run in main.py, will only create the tables and
    the database if they do not already exist.
    '''

    # Open connection to DB_PATH constant
    conn = sqlite3.connect(DB_PATH)
    curs = conn.cursor()

    # Create events table if it doesn't exist
    curs.execute("""
        CREATE TABLE IF NOT EXISTS events (
            Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            event_level TEXT,
            event_name TEXT,
            info TEXT,
            data TEXT
            )
    """)

    # Create Commands table if it doesn't exist
    curs.execute("""
        CREATE TABLE IF NOT EXISTS command_calls (
            Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            command TEXT,
            parameters TEXT,
            user_id TEXT,
            user_name TEXT,
            guild_id TEXT,
            guild_name TEXT
            )
    """)

    # Create yt_downloads table if it doesn't exist
    curs.execute("""
        CREATE TABLE IF NOT EXISTS yt_downloads (
            Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            video_title TEXT,
            video_url TEXT,
            video_length_s REAL,
            download_size_mb REAL,
            download_path TEXT
            )
    """)

    # Close Connection
    conn.commit()
    conn.close()

### ----- MODULE FUNCTIONS ----- ###

def log_command_call(command, ctx_info):

    # Pack values into a tuple
    log_values = (
        command,
        ctx_info.message.content,
        ctx_info.author.id,
        ctx_info.author.name+"#"+ctx_info.author.discriminator,
        ctx_info.guild.id,
        ctx_info.guild.name
    )

    conn = sqlite3.connect(DB_PATH)
    curs = conn.cursor()

    curs.execute('''INSERT INTO command_calls VALUES (datetime(), ?, ?, ?, ?, ?, ?)''', log_values)

    conn.commit()
    conn.close()

def log_event(event_level: string, event_name: string, info: string, data=None):

    # Put parameters into a tuple
    params = (event_level, event_name, info, data)

    # Create Connection and Cursor
    conn = sqlite3.connect(DB_PATH)
    curs = conn.cursor()

    # Create new row
    if data == None:
        curs.execute("INSERT INTO events (Timestamp, event_level, event_name, info) VALUES (datetime(), ?, ?, ?)", params[:-1])
    else:
        curs.execute("INSERT INTO events VALUES (datetime(), ?, ?, ?, ?)", params)

    # Commit and Close connection
    conn.commit()
    conn.close()
