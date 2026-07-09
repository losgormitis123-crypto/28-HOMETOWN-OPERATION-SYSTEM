# GitHub 自动生成视频说明

这个项目已经配置了 GitHub Actions。

上传到 GitHub 后，只要运行 `build-hometown-video` 工作流，就会自动生成一个竖屏字幕视频。

## 会做什么

1. 读取老家清晨田边图片。
2. 读取口播字幕文件。
3. 在 GitHub 服务器安装 Python 图片工具。
4. 把图片和字幕合成一个竖屏 AVI 视频。
5. 把最终视频作为 GitHub Actions 产物保存。

## 最终视频位置

GitHub Actions 跑完后，在工作流页面下载：

`hometown-final-video`

里面的文件是：

`2026-07-09_老家水田_最终成片.avi`

## 说明

这个版本先保证远端稳定生成视频。

后面可以在剪映里导入 AVI，再用自己的声音录一遍，最后导出 MP4。
