# Git 指令大全 📚

## 前言

Git 是目前最流行的分布式版本控制系统，无论你是个人开发者还是团队协作，掌握 Git 都是必备技能。本文将系统整理 Git 的常用指令，从基础到进阶，帮助你在日常开发中快速查阅。

---

## 一、基础配置

### 1.1 用户配置
```bash
# 设置全局用户名和邮箱
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"

# 设置当前项目用户名和邮箱
git config user.name "你的名字"
git config user.email "你的邮箱"

# 查看所有配置
git config --list

# 编辑配置文件
git config --global --edit
```

### 1.2 其他配置
```bash
# 设置默认编辑器
git config --global core.editor "vim"

# 配置别名（提高效率）
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.st status

# 启用颜色显示
git config --global color.ui true
```

---

## 二、仓库操作

### 2.1 初始化仓库
```bash
# 在当前目录初始化仓库
git init

# 初始化指定目录
git init [项目名称]

# 克隆远程仓库
git clone [远程仓库地址]
git clone [远程仓库地址] [本地目录名]
```

### 2.2 查看状态
```bash
# 查看工作区状态
git status
git status -s  # 简洁模式

# 查看提交日志
git log
git log --oneline  # 单行显示
git log --graph    # 图形化显示
git log -p         # 显示详细差异
git log --author="名字"  # 按作者筛选
```

---

## 三、日常操作

### 3.1 添加文件
```bash
# 添加指定文件
git add [文件名]

# 添加所有文件
git add .
git add -A
git add --all

# 添加当前目录所有文件
git add *

# 交互式添加
git add -i
```

### 3.2 提交更改
```bash
# 提交暂存区
git commit -m "提交信息"

# 跳过暂存区直接提交
git commit -a -m "提交信息"

# 修改最后一次提交
git commit --amend -m "新的提交信息"

# 添加遗漏文件到上次提交
git commit --amend --no-edit
```

### 3.3 删除和移动
```bash
# 删除文件
git rm [文件名]
git rm --cached [文件名]  # 仅从暂存区删除

# 移动/重命名文件
git mv [原文件名] [新文件名]
```

---

## 四、分支管理

### 4.1 分支操作
```bash
# 查看分支
git branch              # 本地分支
git branch -r          # 远程分支
git branch -a          # 所有分支

# 创建分支
git branch [分支名]
git checkout -b [分支名]  # 创建并切换

# 切换分支
git checkout [分支名]
git switch [分支名]      # 新版Git

# 合并分支
git merge [分支名]       # 合并到当前分支

# 删除分支
git branch -d [分支名]   # 删除已合并分支
git branch -D [分支名]   # 强制删除未合并分支
```

### 4.2 冲突解决
```bash
# 查看冲突文件
git status

# 解决冲突后
git add [已解决的文件]
git commit -m "解决冲突"

# 中止合并
git merge --abort
```

---

## 五、远程仓库

### 5.1 远程操作
```bash
# 查看远程仓库
git remote -v

# 添加远程仓库
git remote add origin [仓库地址]

# 删除远程仓库
git remote rm [仓库名]

# 重命名远程仓库
git remote rename [原名] [新名]

# 推送代码
git push origin [分支名]
git push -u origin [分支名]  # 首次推送并建立关联
git push --all               # 推送所有分支
git push --tags              # 推送标签

# 拉取代码
git pull origin [分支名]
git fetch origin [分支名]    # 仅获取不合并

# 从远程仓库克隆
git clone [仓库地址]
```

---

## 六、撤销与回退

### 6.1 撤销操作
```bash
# 撤销工作区修改
git checkout -- [文件名]
git restore [文件名]        # 新版Git

# 撤销暂存区
git reset HEAD [文件名]
git restore --staged [文件名]

# 回退版本
git reset --soft [版本号]   # 保留工作区和暂存区
git reset --mixed [版本号]  # 保留工作区，清空暂存区
git reset --hard [版本号]   # 彻底回退

# 撤销提交
git revert [版本号]         # 生成新提交撤销指定提交
```

### 6.2 查看差异
```bash
# 工作区与暂存区差异
git diff

# 暂存区与版本库差异
git diff --cached
git diff --staged

# 工作区与版本库差异
git diff HEAD

# 两个分支差异
git diff [分支1] [分支2]

# 两个提交差异
git diff [版本号1] [版本号2]
```

---

## 七、标签管理

```bash
# 查看标签
git tag
git tag -l "v1.*"

# 创建标签
git tag [标签名]
git tag -a [标签名] -m "标签信息"

# 推送标签
git push origin [标签名]
git push --tags

# 删除标签
git tag -d [标签名]
git push origin :refs/tags/[标签名]  # 删除远程标签

# 检出标签
git checkout [标签名]
```

---

## 八、暂存与清理

```bash
# 暂存当前工作
git stash
git stash save "暂存信息"

# 查看暂存列表
git stash list

# 恢复暂存
git stash pop          # 恢复并删除
git stash apply        # 恢复但不删除
git stash apply stash@{2}  # 恢复指定暂存

# 删除暂存
git stash drop stash@{0}
git stash clear        # 清空所有暂存

# 清理工作区
git clean -n           # 查看将被清理的文件
git clean -f           # 强制清理
git clean -fd          # 清理文件和目录
```

---

## 九、高级操作

### 9.1 变基操作
```bash
# 变基当前分支
git rebase [分支名]

# 交互式变基
git rebase -i HEAD~3    # 修改最近3次提交

# 继续变基
git rebase --continue

# 跳过冲突提交
git rebase --skip

# 中止变基
git rebase --abort
```

### 9.2 拣选提交
```bash
# 将指定提交应用到当前分支
git cherry-pick [版本号]

# 应用多个提交
git cherry-pick [版本号1] [版本号2]

# 继续拣选
git cherry-pick --continue

# 中止拣选
git cherry-pick --abort
```

### 9.3 子模块
```bash
# 添加子模块
git submodule add [仓库地址] [路径]

# 初始化子模块
git submodule init
git submodule update

# 更新所有子模块
git submodule update --init --recursive

# 查看子模块状态
git submodule status
```

---

## 十、实用技巧

### 10.1 常用组合命令
```bash
# 撤销最后一次提交并保留修改
git reset --soft HEAD^

# 修改最新提交信息
git commit --amend -m "新信息"

# 合并多个提交
git rebase -i HEAD~3

# 查找谁修改了代码
git blame [文件名]

# 查看提交历史中的关键词
git log -S "关键词"

# 查看文件修改历史
git log -p [文件名]
```

### 10.2 Git工作流示例
```bash
# 日常开发流程
git pull                    # 更新代码
git checkout -b feature-x   # 创建功能分支
git add .                   # 添加修改
git commit -m "完成功能X"   # 提交代码
git checkout main          # 切回主分支
git pull                   # 更新主分支
git merge feature-x        # 合并功能分支
git push                   # 推送到远程

# 紧急修复流程
git stash                  # 暂存当前工作
git checkout -b hotfix     # 创建修复分支
git add .                  # 添加修复
git commit -m "紧急修复"   # 提交修复
git checkout main          # 切回主分支
git merge hotfix          # 合并修复
git push                  # 推送到远程
git stash pop             # 恢复之前工作
```

---

## 结语

Git 指令虽然多，但常用的其实只有二三十个。建议先从基础指令开始练习，随着使用频率增加，再逐步学习高级功能。记住，Git 最强大的不是单个指令，而是它们之间的组合使用。

> 提示：可以通过 `git help [指令名]` 查看详细帮助文档，或者在终端输入 `git [指令名] -h` 查看简略帮助。

希望这份 Git 指令大全对你有帮助！如果你有任何问题或建议，欢迎在评论区留言交流。Happy coding! 🚀