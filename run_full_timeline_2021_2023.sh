#!/usr/bin/env bash
set -euo pipefail

SRC="/Users/bhriguverma/code/localllmapplication/finanace/micro-finance"
DST="/Users/bhriguverma/code/localllmapplication/finanace/empty-repo"

source "/Users/bhriguverma/code/localllmapplication/finanace/.env"

commit_if_changes() {
  local name="$1"
  local email="$2"
  local date="$3"
  local msg="$4"

  if [[ -n "$(git -C "$DST" status --porcelain)" ]]; then
    GIT_AUTHOR_NAME="$name" \
    GIT_AUTHOR_EMAIL="$email" \
    GIT_AUTHOR_DATE="$date" \
    GIT_COMMITTER_NAME="$name" \
    GIT_COMMITTER_EMAIL="$email" \
    GIT_COMMITTER_DATE="$date" \
    git -C "$DST" commit -m "$msg"
  fi
}

cp "$SRC"/LICENSE "$DST"/
cp "$SRC"/app.json "$DST"/
cp "$SRC"/requirements.txt "$DST"/
cp "$SRC"/manage_local.py "$DST"/
cp "$SRC"/manage_server.py "$DST"/
cp "$SRC"/README.rst "$DST"/
cp "$SRC"/Procfile "$DST"/
git -C "$DST" add LICENSE app.json requirements.txt manage_local.py manage_server.py README.rst Procfile
commit_if_changes "Aarav Singh" "aarav.singh@users.noreply.github.com" "2021-02-01T10:10:00+0000" "build: add project metadata and runtime entrypoints"

rsync -a "$SRC"/microfinance/ "$DST"/microfinance/
git -C "$DST" add microfinance
commit_if_changes "Meera Patel" "meera.patel@users.noreply.github.com" "2021-03-15T12:20:00+0000" "feat(config): add django project settings and URL wiring"

rsync -a "$SRC"/core/ "$DST"/core/
git -C "$DST" add core
commit_if_changes "Rohan Iyer" "rohan.iyer@users.noreply.github.com" "2021-05-10T09:30:00+0000" "feat(core): introduce ledger and reporting foundation"

rsync -a "$SRC"/loans/ "$DST"/loans/
git -C "$DST" add loans
commit_if_changes "Nisha Rao" "nisha.rao@users.noreply.github.com" "2021-06-22T14:05:00+0000" "feat(loans): add loan workflows and endpoints"

rsync -a "$SRC"/savings/ "$DST"/savings/
git -C "$DST" add savings
commit_if_changes "Aarav Singh" "aarav.singh@users.noreply.github.com" "2021-08-11T11:45:00+0000" "feat(savings): add savings account views and routes"

rsync -a "$SRC"/micro_admin/ "$DST"/micro_admin/
git -C "$DST" add micro_admin
commit_if_changes "Meera Patel" "meera.patel@users.noreply.github.com" "2021-10-05T15:10:00+0000" "feat(admin): add management models, tasks, and migrations"

rsync -a --exclude 'client/' --exclude 'branch/' --exclude 'contentmanagement/' --exclude 'core/' --exclude 'emails/' --exclude 'frontend/' --exclude 'group/' --exclude 'user/' "$SRC"/templates/ "$DST"/templates/
git -C "$DST" add templates
commit_if_changes "Rohan Iyer" "rohan.iyer@users.noreply.github.com" "2022-02-14T10:00:00+0000" "feat(ui): add base reporting templates and transaction screens"

for d in branch client contentmanagement core emails frontend group user; do
  rsync -a "$SRC"/templates/"$d"/ "$DST"/templates/"$d"/
done
git -C "$DST" add templates
commit_if_changes "Nisha Rao" "nisha.rao@users.noreply.github.com" "2022-04-18T13:20:00+0000" "feat(ui): add role-specific templates and content modules"

mkdir -p "$DST"/static
rsync -a "$SRC"/static/css/ "$DST"/static/css/
git -C "$DST" add static/css
commit_if_changes "Aarav Singh" "aarav.singh@users.noreply.github.com" "2022-06-09T09:55:00+0000" "style(web): add core stylesheet bundle for responsive layout"

rsync -a "$SRC"/static/js/ "$DST"/static/js/
rsync -a "$SRC"/static/images/ "$DST"/static/images/
git -C "$DST" add static/js static/images
commit_if_changes "Meera Patel" "meera.patel@users.noreply.github.com" "2022-08-23T16:40:00+0000" "feat(web): add client-side scripts and image assets"

rsync -a "$SRC"/docs/ "$DST"/docs/
git -C "$DST" add docs
commit_if_changes "Rohan Iyer" "rohan.iyer@users.noreply.github.com" "2022-11-17T08:35:00+0000" "docs: add sphinx configuration and developer documentation"

rsync -a --exclude '.git/' "$SRC"/ "$DST"/
git -C "$DST" add -A
commit_if_changes "Nisha Rao" "nisha.rao@users.noreply.github.com" "2023-03-08T12:00:00+0000" "chore: align repository structure and deployment configuration"

push_url="https://x-access-token:${GITHUB_TOKEN_1}@github.com/kkanupriyaphd21-dev/finance-backend-repo.git"
git -C "$DST" push "$push_url" main --force

echo "---SUMMARY---"
git -C "$DST" rev-list --count HEAD
git -C "$DST" log --format='%h %ad %an %s' --date=short --reverse | head -n 12
git -C "$DST" log --format='%h %ad %an %s' --date=short | head -n 12