# Shared

`shared/` 存放跨模块或跨阶段复用的共享输入、脱敏 fixtures 和中间产物。

## 推荐子目录

- `shared/raw-inputs/`
  经过授权或脱敏的原始输入样例。
- `shared/fixtures/`
  跨 stack 复用的 fixtures。
- `shared/generated/`
  可重新生成的中间产物或导出样例。

## 约束

- 不要默认放真实客户数据、生产导出、密钥、未脱敏 Excel / CSV。
- 如果材料来自真实数据源，必须在 task boundary 或 data-access evidence 中说明授权、脱敏和使用范围。
- 应用级 fixtures 优先放到 `stack/<project>/fixtures/`；只有跨模块共享时才放到这里。
