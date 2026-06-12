# Migrations

`.gstack/migrations/` 存放 repo-native 迁移计划和迁移记录。

适合放：

- 目录重构计划。
- 旧 baseline 到 `stack/` 的迁移计划。
- framework core 升级计划。
- adapter 合并计划。
- 业务代码迁移计划和回滚说明。

不适合放：

- 真实数据导出。
- 数据库 migration 文件本体，除非 adapter 明确规定这里是工程真源。
- 未确认的一次性聊天草稿。

迁移计划应至少说明：来源、目标、允许改动、禁止改动、验证方式、回滚方式和剩余风险。
