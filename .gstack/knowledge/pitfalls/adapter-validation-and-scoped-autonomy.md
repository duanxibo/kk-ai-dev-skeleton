# 配置校验与目标授权

- adapter 配置必须先校验再归一化，错误字段不能静默转换成空值。
- guard 缺失 adapter 时默认拒绝继续；诊断兼容模式的 warning 不代表 readiness。
- 不把旧项目路径注入通用配置；adapter 的空路径列表必须覆盖 guard 的模板 fallback。
- 任务完成后的下一步建议不构成新任务授权；同一已授权目标内可继续阶段推进。
- CI smoke 使用临时任务状态，清理后不改变开发者的当前任务。
- 合并 evidence 只减少文件数；不能自动把 QA 标记为 done。
