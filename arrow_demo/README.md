# Arrow Demo

一个使用 Cocos Creator 制作的简易飞剑射击小游戏。玩家点击屏幕发射宝剑，将宝剑插入旋转轮盘；成功射入 5 把宝剑则胜利，发射中的宝剑撞到已有宝剑则失败。

## 项目信息

- 引擎：Cocos Creator 3.8.8
- 语言：TypeScript
- 主场景：`assets/scene/C1.scene`
- 主逻辑：`assets/code/player.ts`

## 玩法说明

- 轮盘会持续旋转。
- 点击屏幕发射一把宝剑。
- 宝剑飞到轮盘位置且没有碰撞时，会固定到轮盘上。
- 成功射入一把宝剑后，当前数量加 1。
- 射入 5 把宝剑会判定通关，并显示成功提示。
- 发射中的宝剑碰到已有宝剑会判定失败，并显示失败提示。
- 失败或通关后会停止轮盘和输入。
- 点击重试按钮会重新加载 `C1` 场景，开始新一局。

## 目录结构

```text
assets/
  code/
    player.ts                 # 玩家输入、发射动画、碰撞判断、胜负结算
  scene/
    C1.scene                  # 游戏主场景
  prefab/
    Sword.prefab              # 宝剑预制体
  ui/
    background.png            # 背景图
    turntable.png             # 旋转轮盘图片
    sword.png                 # 宝剑图片
    retry_play_button.png     # 重试按钮图片
    retry_animation.anim      # 重试按钮动画
  audio/
    bgm_loop.wav              # 背景音乐
    arrow_hit.wav             # 发射音效
    success.wav               # 成功音效
    fail.wav                  # 失败音效
tools/
  generate_cartoon_assets.py  # 生成卡通 UI 资源的脚本
  generate_cartoon_audio.py   # 生成音频资源的脚本
settings/
  v2/packages/project.json    # 项目分辨率等配置
package.json                  # Cocos Creator 项目信息
```

## 运行方式

1. 使用 Cocos Creator 3.8.8 打开项目根目录。
2. 打开场景 `assets/scene/C1.scene`。
3. 点击编辑器顶部的预览按钮运行游戏。

## 核心脚本说明

`assets/code/player.ts` 中的 `player` 组件负责：

- 在 `update` 中持续旋转轮盘节点。
- 监听全局触摸输入，并限制同一时间只发射一把宝剑。
- 实例化 `Sword.prefab`，播放发射 tween 动画。
- 监听宝剑 `Collider2D` 的 `BEGIN_CONTACT` 碰撞事件。
- 在宝剑没有碰撞时，将宝剑挂到旋转轮盘节点下并同步世界坐标。
- 更新当前射入数量，并在达到 5 把时显示成功结果。
- 使用 `IsCurrentArrowHit` 和 `IsGameOver` 避免最后一把宝剑碰撞时同时触发成功和失败。
- 播放发射、成功、失败音效。
- 通过 `NEW_GAME` 重新加载主场景。

## 编辑器绑定项

挂载 `player.ts` 的节点需要在 Inspector 中绑定以下属性：

- `Rotate_Node`：旋转轮盘节点
- `Arrow_Top_Node`：宝剑发射时的临时父节点
- `Tip_Node`：成功/失败结果菜单节点
- `Bgm_Node`：背景音乐节点
- `Tip_Label`：结果提示 Label 组件
- `Curr_Count_Label`：当前射入数量 Label 组件
- `Arrow_Prefab`：宝剑预制体
- `Retry_Animation`：重试按钮动画组件
- `Success_Audio`：成功音效
- `Failure_Audio`：失败音效
- `Hit_Audio`：发射音效

如果重新加载场景后某个字段变成 `null`，通常是因为场景没有保存对应的 Inspector 绑定。重新拖拽绑定后，记得保存场景。

## 开发备注

- 当前目标数量写在脚本判断和场景文案中，都是 5 把；如果要调整关卡目标，需要同步修改。
- 胜负结算统一走 `SHOW_RESULT`，避免同一局重复弹出结果。
- 宝剑飞到终点后的成功判断会延后一帧执行，用来等待可能同一帧触发的碰撞事件先完成。
- 当前重新开始游戏使用 `director.loadScene('C1')` 直接重载主场景。
