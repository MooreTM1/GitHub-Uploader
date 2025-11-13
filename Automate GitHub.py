import os
import csv
import shutil
import requests
from pathlib import Path
from slugify import slugify
from git import Repo, GitCommandError

# --- user config ---
BASE_DIR = r"C:\Path\To\Your\Projects"              # parent folder containing project subfolders
SHARED_GITIGNORE = r"C:\Path\To\Shared\.gitignore"  # path to shared .gitignore
FORCE_GITIGNORE = True                              # overwrite .gitignore if one already exists
GITHUB_OWNER = "YourGitHubUsername"                 # or your organization name
OWNER_IS_ORG = False                                # True if creating under an organization
LOG_CSV = os.path.join(BASE_DIR, "GitHub_upload_log.csv")

API_BASE = "https://api.github.com"
CREATE_REPO_ENDPOINT_USER = f"{API_BASE}/user/repos"
CREATE_REPO_ENDPOINT_ORG = f"{API_BASE}/orgs/{GITHUB_OWNER}/repos"

def get_token() -> str:
    tok = os.getenv("GITHUB_TOKEN")
    if not tok:
        raise RuntimeError("Set GITHUB_TOKEN env var with a token that has 'repo' scope.")
    return tok

def sanitize_repo_name(name: str) -> str:
    s = slugify(name, lowercase=True)
    return s or "repo"

def ensure_gitignore(project_dir: Path):
    dest = project_dir / ".gitignore"
    if SHARED_GITIGNORE and os.path.isfile(SHARED_GITIGNORE):
        if FORCE_GITIGNORE or not dest.exists():
            shutil.copyfile(SHARED_GITIGNORE, dest)

def create_private_repo(repo_name: str, token: str) -> dict:
    payload = {
        "name": repo_name,
        "private": True,
        "has_issues": True,
        "has_wiki": False,
        "auto_init": False,
        "delete_branch_on_merge": True,
    }
    url = CREATE_REPO_ENDPOINT_ORG if OWNER_IS_ORG else CREATE_REPO_ENDPOINT_USER
    r = requests.post(url, json=payload, headers={"Authorization": f"token {token}"})
    if r.status_code == 422 and "name already exists" in r.text.lower():
        r2 = requests.get(f"{API_BASE}/repos/{GITHUB_OWNER}/{repo_name}",
                          headers={"Authorization": f"token {token}"})
        if r2.status_code == 200:
            return r2.json()
    if r.status_code != 201:
        raise RuntimeError(f"Create repo failed ({r.status_code}): {r.text}")
    return r.json()  # <-- call the function

def init_commit_push(project_dir: Path, repo_full_name: str, token: str):
    repo = Repo.init(project_dir)

    ensure_gitignore(project_dir)
    repo.git.add(A=True)

    if not repo.is_dirty(untracked_files=True):
        readme = project_dir / "README.md"
        if not readme.exists():
            readme.write_text(f"# {project_dir.name}\n\nInitial import.")
        repo.git.add(A=True)

    try:
        _ = repo.head.commit
    except Exception:
        repo.index.commit("Initial commit")

    try:
        repo.git.branch("-M", "main")
    except GitCommandError:
        pass

    remote_url = f"https://{token}@github.com/{repo_full_name}.git"
    if "origin" in [r.name for r in repo.remotes]:
        repo.delete_remote("origin")
    origin = repo.create_remote("origin", remote_url)
    origin.push("main", set_upstream=True)

def write_log_row(local_folder: str, repo_name: str, html_url: str):
    header_needed = not os.path.exists(LOG_CSV)
    with open(LOG_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if header_needed:
            w.writerow(["local_folder", "repo_name", "github_url"])
        w.writerow([local_folder, repo_name, html_url])

def main():
    token = get_token()
    base = Path(BASE_DIR)
    if not base.exists():
        raise FileNotFoundError(f"Base directory not found: {BASE_DIR}")
    
    skip_names = {".git", ".vs", "__pycache__", "node_modules"}

    print(f"Scanning: {BASE_DIR}")
    for project_dir in sorted([p for p in base.iterdir() if p.is_dir()]):
        if project_dir.name.lower() in skip_names:
            continue
        if (project_dir / ".git").exists():
            print(f"- SKIP (already a git repo): {project_dir.name}")
            continue

        repo_name = sanitize_repo_name(project_dir.name)  # <-- pass a string
        repo_full_name = f"{GITHUB_OWNER}/{repo_name}"

        print(f"\n=== {project_dir.name} -> {repo_full_name} ===")

        info = create_private_repo(repo_name, token)
        html_url = info.get("html_url", f"https://github.com/{repo_full_name}")
        print(f"Repo ready: {html_url}")

        init_commit_push(project_dir, repo_full_name, token)
        print(f"Pushed main: {html_url}")

        write_log_row(str(project_dir), repo_name, html_url)

    print("\nDone. Mapping written to:", LOG_CSV)

if __name__ == "__main__":
    main()