import subprocess

def run_tree(directory_path, level):
    try:
        # Command to run: tree -L <level> <directory_path>
        result = subprocess.run(
            ["tree", "-L", str(level), directory_path],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running tree: {e}")
    except FileNotFoundError:
        print("The 'tree' command is not installed on this system.")

# Example usage: display structure to depth of 2
run_tree(".", 2)
