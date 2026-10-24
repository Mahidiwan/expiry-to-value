
import streamlit as st
import mysql.connector


def get_connection():
    db_config = st.secrets["mysql"]

    connection = mysql.connector.connect(
        host=db_config["host"],
        port=int(db_config.get("port", 3306)),
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"],
    )

    return connection
