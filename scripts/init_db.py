from app.db.schema import init_database


if __name__ == "__main__":
    init_database()

    print(
        "KnowFlow database initialized."
    )