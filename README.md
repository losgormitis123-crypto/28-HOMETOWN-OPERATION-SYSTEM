# AI返乡计划自运营系统

这是一个为普通父亲打造的AI原生内容运营系统。

核心不是做三农账号，也不是做AI教学账号。

而是通过AI记录湖北老家的牛羊生活、童年记忆、家人生活和个人成长，最终形成一套留给孩子的数字家书。

## 一句话定位

离家18年，我用AI把湖北老家的牛羊生活，做成留给孩子的数字家书。

## 系统目标

1. 建立家乡素材库
2. 建立个人记忆库
3. 建立长期内容库
4. 建立数据复盘机制
5. 建立AI辅助成长系统

## 当前阶段

V1.0 MVP阶段

只做最小闭环：

素材 -> 选题 -> 内容 -> 审核 -> 发布 -> 数据 -> 复盘

## 核心原则

真实第一。

长期第一。

家乡第一。

孩子视角第一。

人生选择权第一。

## 使用方式

1. 把家人发来的照片、视频、语音、文字放入 `00_INPUT/`。
2. 按 `03_MATERIAL_DATABASE/material_naming_rules.md` 改好文件名。
3. 在 `03_MATERIAL_DATABASE/material_database.csv` 登记素材。
4. 用 `10_AI_ROLES/` 里的AI角色Prompt分析素材、生成选题、生成内容、审核内容。
5. 发布后在 `07_PUBLISH_SYSTEM/publish_record.csv` 记录。
6. 第二天在 `08_DATA_SYSTEM/daily_data.csv` 补充数据。
7. 每周使用 `09_REVIEW_SYSTEM/` 和 `11_WORKFLOWS/weekly_workflow.md` 复盘。

