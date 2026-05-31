# GitHub Publishing

This repo is intended to be pushed as a Docker-first application repository.

## Recommended Repo Name

```text
cloud_infra
```

## Before Pushing

Check that real secrets are not tracked:

```bash
git status --short
git ls-files .env .env.prod .env.local
```

The following should remain untracked/ignored:

```text
.env
.env.prod
.env.local
*.pem
*.key
```

## Push

```bash
git add -A
git commit -m "Prepare Docker microservice application"
git remote add cloud_infra https://github.com/<owner>/cloud_infra.git
git push -u cloud_infra main
```
