#!/usr/bin/env bash
# Deploy ritikasartbook.com to GitHub Pages.
#
#   bash tools/deploy.sh                      # repo + push + Pages (github.io URL)
#   SET_CUSTOM_DOMAIN=1 bash tools/deploy.sh  # ...and point ritikasartbook.com at it
#
# Override defaults:
#   REPO=my-repo BRANCH=main bash tools/deploy.sh
#
# Stage 1 (default) publishes to https://<owner>.github.io/<repo>/ with no CNAME
# file, so the preview works immediately without any DNS setup.
# Stage 2 (SET_CUSTOM_DOMAIN=1) drops in the CNAME file and sets the custom
# domain on the Pages config — run it once your DNS records resolve.
set -euo pipefail

REPO="${REPO:-ritikasartbook}"
BRANCH="${BRANCH:-main}"
SET_CUSTOM_DOMAIN="${SET_CUSTOM_DOMAIN:-0}"
TOOLS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOMAIN="$(tr -d '[:space:]' < "$TOOLS/CNAME.custom-domain")"
OWNER="$(gh api user --jq .login)"
ROOT="$(cd "$TOOLS/.." && pwd)"

cd "$ROOT"

echo "==> GitHub account : $OWNER"
echo "==> Repo target    : $OWNER/$REPO  (branch $BRANCH)"
if [ "$SET_CUSTOM_DOMAIN" = "1" ]; then
  echo "==> Custom domain  : $DOMAIN"
else
  echo "==> Custom domain  : none (github.io preview)"
fi
echo

# ---------------------------------------------------------------- 1. repo ----
if gh repo view "$OWNER/$REPO" >/dev/null 2>&1; then
  echo "==> Repo already exists, reusing it."
else
  echo "==> Creating public repo $OWNER/$REPO ..."
  gh repo create "$OWNER/$REPO" \
    --public \
    --description "Whimsical children's book illustration, book cover, character design & surface pattern portfolio" \
    --disable-wiki
fi

# --------------------------------------------------- 2. custom domain file ----
if [ "$SET_CUSTOM_DOMAIN" = "1" ]; then
  echo "==> Writing CNAME ($DOMAIN)"
  printf '%s\n' "$DOMAIN" > CNAME
elif [ -f CNAME ]; then
  echo "==> Removing CNAME so the github.io URL works without DNS."
  rm -f CNAME
fi

# ------------------------------------------------------- 3. commit + push ----
git init -q 2>/dev/null || true
git symbolic-ref -q HEAD >/dev/null 2>&1 || git checkout -q -b "$BRANCH"
git add -A
if git diff --cached --quiet; then
  echo "==> Nothing new to commit."
else
  git -c user.name="${GIT_NAME:-$OWNER}" \
      -c user.email="${GIT_EMAIL:-$OWNER@users.noreply.github.com}" \
      commit -q -m "Portfolio site for ritikasartbook"
  echo "==> Committed."
fi

if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "https://github.com/$OWNER/$REPO.git"
else
  git remote add origin "https://github.com/$OWNER/$REPO.git"
fi

git push -u origin "$BRANCH"
echo "==> Pushed to origin/$BRANCH"

# -------------------------------------------------------- 4. enable Pages ----
echo "==> Enabling GitHub Pages on $BRANCH / ..."
gh api -X POST "repos/$OWNER/$REPO/pages" \
  -f "source[branch]=$BRANCH" -f "source[path]=/" >/dev/null 2>&1 \
  || gh api -X PUT "repos/$OWNER/$REPO/pages" \
       -f "source[branch]=$BRANCH" -f "source[path]=/" >/dev/null

# ------------------------------------------------------- 5. custom domain ----
if [ "$SET_CUSTOM_DOMAIN" = "1" ]; then
  echo "==> Setting custom domain $DOMAIN ..."
  gh api -X PUT "repos/$OWNER/$REPO/pages" -f "cname=$DOMAIN" >/dev/null || \
    echo "   (set it later in Settings > Pages if this step failed)"
fi

echo
echo "==> Done."
echo "    Pages URL : https://$OWNER.github.io/$REPO/"
if [ "$SET_CUSTOM_DOMAIN" = "1" ]; then
  echo "    Custom    : https://$DOMAIN/"
fi
echo

if [ "$SET_CUSTOM_DOMAIN" != "1" ]; then
  cat <<EOF
Next, when you are ready for ritikasartbook.com:

  1. Add these DNS records at your registrar:
       A      @      185.199.108.153
       A      @      185.199.109.153
       A      @      185.199.110.153
       A      @      185.199.111.153
       CNAME  www    $OWNER.github.io
  2. Once DNS resolves, switch the domain on:
       SET_CUSTOM_DOMAIN=1 bash tools/deploy.sh
  3. In Settings > Pages, tick "Enforce HTTPS".
EOF
else
  echo "Remember to tick 'Enforce HTTPS' in Settings > Pages once the cert is issued."
fi
