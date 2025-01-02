#!/bin/bash

# 检查是否安装了gh
if ! command -v gh &> /dev/null; then
    echo "GitHub CLI (gh) 未安装"
    echo "安装说明: https://cli.github.com/manual/installation"
    exit 1
fi

# 检查是否登录
if ! gh auth status &> /dev/null; then
    echo "请先登录GitHub:"
    gh auth login
fi

# 创建仓库
read -p "仓库名称: " repo_name
description=""
is_private="y"

private_flag=""
if [ "$is_private" = "y" ]; then
    private_flag="--private"
else
    private_flag="--public"
fi

# 创建仓库
gh repo create "$repo_name" $private_flag --description "$description"

# 初始化本地仓库
git init
echo "# $repo_name" > README.md
git add README.md
git add --all
git commit -m "Initial commit"
git branch -M main
git remote add origin "https://github.com/$(gh api user -q .login)/$repo_name.git"
git push -u origin main

echo "仓库已创建: $repo_name"