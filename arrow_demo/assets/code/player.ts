import { _decorator, Component, Node, Prefab, Label, Animation, AudioClip, AudioSource, instantiate, director, input, Input, tween, Vec3, Collider2D, Contact2DType } from 'cc';
const { ccclass, property } = _decorator;

@ccclass('player')
export class player extends Component {
    @property(Node)
    Rotate_Node: Node = null

    @property(Node)
    Arrow_Top_Node: Node = null

    @property(Node)
    Tip_Node: Node = null

    @property(Node)
    Bgm_Node: Node = null

    @property(Label)
    Tip_Label: Label = null

    @property(Label)
    Curr_Count_Label: Label = null

    @property(Prefab)
    Arrow_Prefab: Prefab = null

    @property(Animation)
    Retry_Animation: Animation = null

    @property(AudioClip)
    Success_Audio: AudioClip = null

    @property(AudioClip)
    Failure_Audio: AudioClip = null

    @property(AudioClip)
    Hit_Audio: AudioClip = null

    Arrow_Node: Node = null

    Rotate_Speed: number = 50

    Angle: number = 0

    IsArrowing: boolean = false

    Move: boolean = true

    Curr_Count: number = 0

    IsCurrentArrowHit: boolean = false

    IsGameOver: boolean = false

    start() {}

    update(deltaTime: number) {
        if (!this.Move) return
        if (this.Angle >= 360) this.Angle = 0
        this.Angle += deltaTime * this.Rotate_Speed
        this.Rotate_Node.angle = this.Angle
    }

    protected onLoad() {
        this.Tip_Node.active = false
        input.on(Input.EventType.TOUCH_START, this.TOUCH_START, this)
    }

    protected onDestroy() {
        input.off(Input.EventType.TOUCH_START, this.TOUCH_START, this)
    }

    TOUCH_START() {
        if (!this.Move) return
        if (this.IsGameOver) return
        if (this.IsArrowing) return
        this.IsArrowing = true
        this.IsCurrentArrowHit = false
        this.Arrow_Node = instantiate(this.Arrow_Prefab)
        this.Arrow_Node.setParent(this.Arrow_Top_Node)
        this.Arrow_Node.getComponent(Collider2D).on(Contact2DType.BEGIN_CONTACT, this.ARROW_CONTACT, this)
        const Audio = this.node.getComponent(AudioSource)
        Audio.clip = this.Hit_Audio
        Audio.play()
        tween(this.Arrow_Node)
            .to(0.2, { position: new Vec3(-6, 60, 0) })
            .call(() => {
                this.scheduleOnce(() => {
                    if (this.IsCurrentArrowHit || this.IsGameOver) return
                    // 铆钉轮盘
                    const worldPosition = this.Arrow_Node.getWorldPosition()
                    this.Arrow_Node.setParent(this.Rotate_Node)
                    this.Arrow_Node.setWorldPosition(worldPosition)
                    this.Arrow_Node.angle -= this.Angle
                    this.IsArrowing = false
                    // 更新目标
                    this.Curr_Count++
                    this.Curr_Count_Label.string = "当前：" + this.Curr_Count + "把"
                    if (this.Curr_Count >= 5) {
                        this.SHOW_RESULT(true)
                    }
                }, 0)
            })
            .start()
    }

    ARROW_CONTACT(e) {
        if (this.IsGameOver) return
        this.IsCurrentArrowHit = true
        this.IsArrowing = false
        this.SHOW_RESULT(false)
    }

    SHOW_RESULT(isSuccess: boolean) {
        if (this.IsGameOver) return
        this.IsGameOver = true
        this.Move = false
        this.Tip_Node.active = true
        this.Tip_Label.string = isSuccess ? '成功了' : '失败了'
        this.Retry_Animation.play('retry_animation')
        const Audio = this.node.getComponent(AudioSource)
        Audio.clip = isSuccess ? this.Success_Audio : this.Failure_Audio
        Audio.play()
    }

    NEW_GAME() {
        director.loadScene('C1')
    }
}
