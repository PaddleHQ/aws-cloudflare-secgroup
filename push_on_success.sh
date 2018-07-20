#!/bin/bash -e
#
# Based on https://github.com/Shippable/support/issues/1052
#
# * we don't do force pushes ; that ensures that we can't go backwards
#   or overwrite things if we accidentally (or deliberately to check
#   something) rerun an old commit.
#

git config user.name "Shippable Bot For Paddle"
git config user.email "mdlr@paddle.com"

git remote -v show


if [ "$BRANCH" == "devel" ] && [ "$PULL_REQUEST" == false ]; then
  git checkout -B tested
  git push -u origin tested
fi;

if [ "$BRANCH" == "test_devel" ] && [ "$PULL_REQUEST" == false ]; then
  git checkout -B test_tested
  git push -u origin test_tested
fi;

