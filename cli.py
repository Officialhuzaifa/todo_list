import sqlite3

DB_FILE = "todo_db.sqlite"

# ------------------------------
# DB Helper functions
# ------------------------------
def get_connection():
    try:
        return sqlite3.connect(DB_FILE)
    except sqlite3.Error as e:
        print(f" Database connection error: {e}")
        return None

def create_table():
    con = sqlite3.connect("todo_db.sqlite")
    try:
        cursor = con.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL
            )
        """)
        con.commit()
    finally:
        cursor.close()
        con.close()


def create_task(title, description, status="pending"):
    con = get_connection()
    if not con:
        return
    try:
        cursor = con.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, description, status) VALUES (?, ?, ?)",
            (title, description, status)
        )
        con.commit()
        print(f"Task added successfully! ID: {cursor.lastrowid}")
    finally:
        cursor.close()
        con.close()

def read_tasks():
    con = get_connection()
    if not con:
        return []
    try:
        cursor = con.cursor()
        cursor.execute("SELECT * FROM tasks")
        rows = cursor.fetchall()
        tasks = []
        for row in rows:
            tasks.append({
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "status": row[3]
            })
        return tasks
    finally:
        cursor.close()
        con.close()

def update_task(task_id, title, description, status):
    con = get_connection()
    if not con:
        return
    try:
        cursor = con.cursor()
        cursor.execute(
            "UPDATE tasks SET title=?, description=?, status=? WHERE id=?",
            (title, description, status, task_id)
        )
        con.commit()
        if cursor.rowcount > 0:
            print("✅ Task updated successfully!")
        else:
            print("❌ No task found with that ID.")
    finally:
        cursor.close()
        con.close()

def delete_task(task_id):
    con = get_connection()
    if not con:
        return
    try:
        cursor = con.cursor()
        cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        con.commit()
        if cursor.rowcount > 0:
            print("✅ Task deleted successfully!")
        else:
            print("❌ No task found with that ID.")
    finally:
        cursor.close()
        con.close()

# ------------------------------
# CLI Menu
# ------------------------------
def main():
    create_table()  # Ensure table exists

    while True:
        print("\n📋 TO-DO LIST MENU")
        print("1. Add Task")
        print("2. View Tasks")
        print("3. Update Task")
        print("4. Delete Task")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ").strip()

        if choice == "1":
            title = input("Enter task title: ").strip()
            description = input("Enter task description: ").strip()
            create_task(title, description)

        elif choice == "2":
            tasks = read_tasks()
            if tasks:
                print("\n--- TASKS ---")
                for task in tasks:
                    print(f"ID: {task['id']} | Title: {task['title']} | Description: {task['description']} | Status: {task['status']}")
            else:
                print("No tasks found.")

        elif choice == "3":
            task_id = input("Enter Task ID to update: ").strip()
            if not task_id.isdigit():
                print("❌ Invalid ID. Must be a number.")
                continue
            task_id = int(task_id)
            new_title = input("Enter new title: ").strip()
            new_description = input("Enter new description: ").strip()
            new_status = input("Enter new status (pending/completed): ").strip().lower()
            if new_status not in ["pending", "completed"]:
                print("❌ Status must be 'pending' or 'completed'.")
                continue
            update_task(task_id, new_title, new_description, new_status)

        elif choice == "4":
            task_id = input("Enter Task ID to delete: ").strip()
            if not task_id.isdigit():
                print("❌ Invalid ID. Must be a number.")
                continue
            delete_task(int(task_id))

        elif choice == "5":
            print("👋 Exiting program... Bye!")
            break

        else:
            print("❌ Invalid choice. Please enter a number from 1-5.")
if __name__ == "__main__":
    create_table()   # <-- important
    main()

