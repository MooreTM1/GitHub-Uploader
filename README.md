# GitHub-Uploader
A lightweight automation script that creates a separate GitHub repository for each
project folder under a specified directory. Each repository can be private or public,
includes a shared .gitignore, intitalizes Git, commits project files, and pushes them to GitHub automatically.

# ✨Features
- Scans a chosen base directory for project subfolders.
- Creates a new GitHub repository for each project.
- Supports private or public repositories ("private": True/False).
- Copies a shared .gitignore into each project with optional overwriting.
- Initializes, commits, and pushes code to a new repo.
- Renames the default branch to main.
- Logs results to a CSV file with the headers "local_folder", "repo_name", and "github_url"


# 🧩Requirements
- Python 3.10+
- Git installed and available on your system PATH
- Python libraries: pip install requests gitpython python-slugify
- A GitHub Personal Access Token (PAT) with the following scope:
    - repo (required)

# ⚙️Configuration
- Edit the configuration variables at the top of the script:

<img width="572" height="102" alt="User Config" src="https://github.com/user-attachments/assets/1dcf1508-8461-4357-af74-0876e53056d9" />

# 🌎Making Repositories Public
Inside the "create_private_repo()" function, change:

<img width="92" height="16" alt="True" src="https://github.com/user-attachments/assets/f95573a0-bfe6-4841-90ad-d574d34481d0" />

to

<img width="100" height="14" alt="False" src="https://github.com/user-attachments/assets/ec18925a-1fd0-4afe-85b4-5e9c0b1baf4f" />

Your repositories are now public.

# 🔐Setting Your GitHub Token
1.) **Create A Personal Access Token (PAT)**

Setting -> Developer settings -> Personal access tokens -> Tokens (classic).

2.) **Generate a token with** 

repo (required).

3.) Save the token securely as an environment variable (**DO NOT HARD CODE IT**):

**Windows Powershell:**

setx GITHUB_TOKEN "ghp_your_actual_token_here"

$env:GITHUB_TOKEN="ghp_your_actual_token_here"

**macOS / Linux:**

export GITHUB_TOKEN="ghp_your_actual_token_here"

# 📄.gitignore Usage
The script copies your shared .gitignore to each project directory. If "FORCE_GITIGNORE = True", it will overwrite any existing .gitignore.

Some recommended enteries for C#, .NET, or Visual Studio projects:

- bin/
- obj/
- .vs/
- packages/
- /packages/
- *.nupkg
