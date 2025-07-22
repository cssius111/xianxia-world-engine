# 贡献指南

## 推送流程示例

在确保本地分支已经同步远端的情况下，可以按照以下步骤更新并推送代码：

```bash
git fetch origin
git rebase origin/main
git push origin main --force-with-lease
```

如果仓库需要历史重写（例如进行 LFS 迁移）时，请务必先与团队成员沟通，确认所有人都已准备好再执行上述流程。

请所有协作者遵守此流程，以保持提交历史的整洁。

## 更新 DeepSource 基准

项目使用 [DeepSource](https://deepsource.com/) 进行静态分析。若需要调整
`.deepsource.toml` 的 `[ignore_rules]` 或其他阈值，请在本地安装 DeepSource
CLI 并重新生成基准：

```bash
# 安装 CLI（如未安装）
pip install deepsource-cli

# 重新计算基准并更新配置
deepsource-cli reset-baseline
```

执行完毕后将更新后的 `.deepsource.toml` 提交至仓库，以便团队成员共用同一
基准。
