import subprocess
import os

def run_server():
    """Run the server from its directory."""
    # Define the server's directory and script path
    project_root = os.path.dirname(os.path.abspath(__file__))
    server_dir = os.path.join(project_root, 'src', 'scrape_any_crawler', 'factories')
    server_script = os.path.join(server_dir, 'server.py')
    python_exec = os.path.join(project_root, 'venv', 'bin', 'python')

    # Check if the virtual environment Python binary exists
    if not os.path.exists(python_exec):
        print(f"Error: {python_exec} does not exist. Ensure the virtual environment is set up correctly.")
        return

    # Add project root to PYTHONPATH to resolve imports properly
    os.environ['PYTHONPATH'] = project_root + ':' + os.environ.get('PYTHONPATH', '')

    # Print the server startup information
    print(f"Starting server from: {server_script}")

    # Run the server script without changing the current directory
    subprocess.call([python_exec, server_script])


def run_ui():
    """Run the UI."""
    # Get the project root directory and set paths dynamically
    project_root = os.path.dirname(os.path.abspath(__file__))
    ui_path = os.path.join(project_root, 'ui', 'scrape-any-web')

    # Check if the UI directory exists
    if not os.path.exists(ui_path):
        print(f"Error: {ui_path} does not exist. Ensure the UI project is set up correctly.")
        return

    # Print the UI startup information
    print(f"Starting UI from: {ui_path}")

    # Run npm command without changing the current directory
    subprocess.call(['npm', 'run', 'dev'], cwd=ui_path)


if __name__ == '__main__':
    # Run both the server and UI in parallel or one after the other
    choice = input("Enter '1' to run server, '2' to run UI, or '3' to run both: ").strip()

    if choice == '1':
        run_server()
    elif choice == '2':
        run_ui()
    elif choice == '3':
        # Run both the server and UI concurrently using threads
        from threading import Thread

        # Start server and UI in parallel threads
        server_thread = Thread(target=run_server)
        ui_thread = Thread(target=run_ui)

        server_thread.start()
        ui_thread.start()

        # Wait for both to complete
        server_thread.join()
        ui_thread.join()
    else:
        print("Invalid choice! Exiting.")
