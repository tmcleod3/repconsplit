import os
from pathspec import PathSpec

# Directory containing the Git repo
repo_dir = "/Users/thomasmcleod/Projects/trading_system"

# Path to .gitignore
gitignore_path = os.path.join(repo_dir, ".gitignore")

# Directory to store the output Markdown files
output_dir = os.path.join(repo_dir, "trainers")
os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist

# Temporary full output file
full_output_file = os.path.join(output_dir, "consolidated_repository_full.md")

# Read .gitignore and compile rules
if os.path.exists(gitignore_path):
    with open(gitignore_path, "r", encoding="utf-8") as f:
        gitignore_rules = f.read()
    spec = PathSpec.from_lines("gitwildmatch", gitignore_rules.splitlines())
else:
    spec = PathSpec.from_lines("gitwildmatch", [])

def should_ignore(file_path):
    """Check if a file is ignored based on .gitignore."""
    relative_path = os.path.relpath(file_path, repo_dir)
    # Explicitly ignore `.git` folders
    if ".git" in relative_path.split(os.sep):
        return True
    return spec.match_file(relative_path)

def escape_markdown(text):
    """Escape characters that interfere with Markdown rendering."""
    return text.replace("`", "\\`")

# Step 1: Create a full consolidated Markdown file
with open(full_output_file, "w", encoding="utf-8") as md_file:
    md_file.write("# Consolidated Repository\n\n")
    
    for root, _, files in os.walk(repo_dir):
        # Skip any `.git` directories
        if ".git" in root.split(os.sep):
            print(f"Skipping .git directory: {root}")
            continue

        for file in files:
            file_path = os.path.join(root, file)
            
            # Skip ignored files
            if should_ignore(file_path):
                print(f"Skipping ignored file: {file_path}")
                continue

            try:
                # Write file header
                md_file.write(f"## {os.path.relpath(file_path, repo_dir)}\n\n")
                
                # Read and escape file content
                with open(file_path, "r", encoding="utf-8") as infile:
                    content = infile.read()
                    md_file.write("```plaintext\n")
                    md_file.write(escape_markdown(content))
                    md_file.write("\n```\n\n")
            except Exception as e:
                print(f"Could not read file {file_path}: {e}")
                md_file.write(f"**Could not read file {os.path.relpath(file_path, repo_dir)}**\n\n")

print(f"Full Markdown file created at: {full_output_file}")

# Step 2: Split the full file into chunks of 500 lines
def split_file(input_file, output_dir, line_limit=500):
    with open(input_file, "r", encoding="utf-8") as infile:
        lines = infile.readlines()
    
    part_number = 1
    for i in range(0, len(lines), line_limit):
        chunk = lines[i:i + line_limit]
        part_file = os.path.join(output_dir, f"consolidated_repository_part_{part_number}.md")
        with open(part_file, "w", encoding="utf-8") as part_md_file:
            part_md_file.writelines(chunk)
        print(f"Created file: {part_file}")
        part_number += 1

split_file(full_output_file, output_dir)
