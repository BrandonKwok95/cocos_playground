# Racing Demo

一个使用 Cocos Creator 制作的简易 3D 赛车小游戏。玩家控制赛车在赛道上前进，左右躲避障碍，到达终点则胜利，撞到障碍则失败。

## 项目信息

- 引擎：Cocos Creator 3.8.8
- 语言：TypeScript
- 主场景：`assets/scene/C1.scene`
- 主逻辑：`assets/code/player.ts`

## 玩法说明

- 赛车会自动向前行驶。
- 按 `A` 键向左移动。
- 按 `D` 键向右移动。
- 撞到普通障碍物会失败。
- 撞到 `EndWall` 会判定通关。
- 失败或通关后会显示菜单文字。
- 点击菜单按钮会重置赛车、相机和移动状态，重新开始游戏。

## 目录结构

```text
assets/
  code/
    player.ts                 # 玩家控制、碰撞判断、重开逻辑
  scene/
    C1.scene                  # 游戏主场景
  models/
    light_blue_racer.glb      # 赛车模型
    warning_red_racer.glb     # 赛车/障碍相关模型
  material/
    Track.mtl                 # 赛道材质
  ui/
    racing_track_bg.png       # UI 背景图
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

- 读取键盘输入，记录左右移动方向。
- 在 `update` 中持续移动赛车和相机。
- 限制赛车横向移动范围。
- 监听赛车碰撞体的 `onTriggerEnter` 事件。
- 根据碰撞对象名称判断成功或失败。
- 显示菜单节点并更新结果文字。
- 在 `Init` 方法中重置游戏状态。

## 编辑器绑定项

挂载 `player.ts` 的节点需要在 Inspector 中绑定以下属性：

- `Camera_Node`：主相机节点
- `Car_Node`：赛车节点
- `Car_Collider`：赛车上的碰撞体组件
- `Menu_Node`：结果菜单节点
- `Menu_Text`：结果文字 Label 组件

如果重新加载场景后某个字段变成 `null`，通常是因为场景没有保存对应的 Inspector 绑定。重新拖拽绑定后，记得保存场景。

## 开发备注

- 当前重新开始游戏使用的是状态重置方式，不重新调用 `director.loadScene`。
- 如果后续改回重新加载场景，需要确保 `C1.scene` 已保存所有节点引用。
- 碰撞成功条件依赖节点名称 `EndWall`，如果修改终点节点名称，需要同步修改脚本判断。

