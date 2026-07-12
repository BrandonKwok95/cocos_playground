import { _decorator, Component, Input, input, Node, Collider, Label, director } from 'cc';
const { ccclass, property } = _decorator;

@ccclass('player')
export class player extends Component {
    @property()
    Player_Speed: number = 20

    @property(Node)
    Camera_Node: Node = null

    @property(Node)
    Car_Node: Node = null

    @property(Collider)
    Car_Collider: Collider = null

    @property(Node)
    Menu_Node: Node = null

    @property(Label)
    Menu_Text: Label = null


    Move = true

    Player_Move = { left: false, right: false }


    start() {}

    update(deltaTime: number) {
        if (!this.Move) return
        const currPosition = this.Car_Node.getPosition()
        const cameraPosition = this.Camera_Node.getPosition()

        if (currPosition.z < -390) return;
        let x = currPosition.x
        const y = currPosition.y
        const offset = deltaTime * this.Player_Speed
        const z = currPosition.z - offset
        if (this.Player_Move.left && !this.Player_Move.right) {
            x -= offset
        } else if (this.Player_Move.right && !this.Player_Move.left) {
            x += offset
        }
        if (x >= 3) {
            x = 3
        } else if (x <= -3) {
            x = -3
        }
        this.Car_Node.setPosition(x, y, z)
        this.Camera_Node.setPosition(cameraPosition.x, cameraPosition.y, cameraPosition.z - offset)
    }

    protected onLoad() {
        this.Menu_Node.active = false
        this.Car_Collider = this.Car_Node.getComponent(Collider)
        input.on(Input.EventType.KEY_DOWN, this.Key_Down, this)
        this.Car_Collider.on('onTriggerEnter', this.Collision_Enter, this);
    }

    protected onDestroy() {
        input.off(Input.EventType.KEY_DOWN, this.Key_Down, this)
        this.Car_Collider.off('onTriggerEnter', this.Collision_Enter, this);
    }

    Init(e, customData: unknown) {
        console.log(e, customData)
        this.Move = true
        this.Menu_Node.active = false
        this.Car_Node.setPosition(0, 0, 0)
        this.Camera_Node.setPosition(0, 19, 42)
        this.Player_Move = { left: false, right: false }
        // director.loadScene('C1')
    }

    Key_Down(e) {
        if (e.keyCode === 65) {
            this.Player_Move = { left: true, right: false }
        } else if (e.keyCode === 68) {
            this.Player_Move = { left: false, right: true }
        }
    }
    Collision_Enter(e) {
        console.log('发生碰撞', this.Menu_Node)
        this.Move = false
        this.Menu_Node.active = true
        if (e.otherCollider.node.name === 'EndWall') {
            this.Menu_Text.string = '恭喜，已成功完成'
        } else {
            this.Menu_Text.string = '很遗憾，失败了'
        }
    }
}


