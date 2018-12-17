#!/bin/bash -e
#
# Based on https://github.com/Shippable/support/issues/1052
#
# * we don't do force pushes ; that ensures that we can't go backwards
#   or overwrite things if we accidentally (or deliberately to check
#   something) rerun an old commit.
#

git config user.name "GitHub Travis-CI User"
git config user.email "engineering+travis@paddle.com"

GIT_SSH_COMMAND="ssh -i deploy_key -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" git remote add pushable git@github.com:PaddleHQ/aws-cloudflare-secgroup.git 

git remote -v show

if [[ "$TRAVIS_BRANCH" =~ "devel" ]] && [ "$TRAVIS_PULL_REQUEST" == false ]; then
  git checkout -B tested
  GIT_SSH_COMMAND="ssh -i deploy_key -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" git push -u pushable tested
  exit(0)
else
  exit(1)
fi;
