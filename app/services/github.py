from github import Github, Auth
import requests

class GithubService:
    def __init__(self, access_token: str):
        if not access_token or not access_token.strip():
            raise ValueError("GitHub access token is required")
        auth = Auth.Token(access_token.strip())
        self._g = Github(auth=auth)
        self._access_token = access_token.strip()

    def get_repo_pr(self, pr_url:str):
        owner = pr_url.rstrip("/").split("/")[-4]
        repo = pr_url.rstrip("/").split("/")[-3]
        number = pr_url.rstrip("/").split("/")[-1]
        repository = self._g.get_repo(f"{owner}/{repo}")
        return repository.get_pull(int(number))

    def get_pr_diff(self,pr_url:str):
        owner = pr_url.rstrip("/").split("/")[-4]
        repo = pr_url.rstrip("/").split("/")[-3]
        number = pr_url.rstrip("/").split("/")[-1]
        repository = self._g.get_repo(f"{owner}/{repo}")
        pr = repository.get_pull(int(number))
        response = requests.get(pr.url,headers={
            "Accept": "application/vnd.github.v3.diff",
            "Authorization": f"Bearer {self._access_token}"
        })
        response.raise_for_status()
        return response.text
    
    def comment_on_pr(self,pr_url:str,comment:str):
        owner = pr_url.rstrip("/").split("/")[-4]
        repo = pr_url.rstrip("/").split("/")[-3]
        number = pr_url.rstrip("/").split("/")[-1]
        repository = self._g.get_repo(f"{owner}/{repo}")
        pr = repository.get_pull(int(number))
        pr.create_issue_comment(comment)