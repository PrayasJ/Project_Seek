extends KinematicBody2D

var id = null
var speed = 150
var velocity = Vector2()

#export var weapons = ["flashlight", "handgun", "knife", "rifle", "shotgun"]
export var weapons = ["handgun", "knife"]
signal moveplayer(x,y,rot)
#melee, knife, rifle, shotgun, handgun

var melee = load("res://assets/sfx/melee.wav")
var run = load("res://assets/sfx/run.wav")
var walk = load("res://assets/sfx/footstep.wav")
var handgun = load("res://assets/sfx/handgun.wav")
var machinegun = load("res://assets/sfx/machine-gun.wav")
var rifle = load("res://assets/sfx/rifle.wav")
var knife = load("res://assets/sfx/knife.wav")
var reload = load("res://assets/sfx/reload.wav")
var hit = load("res://assets/sfx/hit.wav")

func init(ID):
	id = ID
	position.x = 0
	position.y = 0

func getID():
	return id

func getx():
	return position.x

func gety():
	return position.y

func _input(event):
	if event.is_action_pressed('scroll_up'):
		$Camera2D.zoom = $Camera2D.zoom - Vector2(0.1, 0.1)
	if event.is_action_pressed('scroll_down'):
		$Camera2D.zoom = $Camera2D.zoom + Vector2(0.1, 0.1)
	
func hit_sfx():
	$sfx.set_stream(hit)

func get_input():
	$player.look_at(get_global_mouse_position())
	velocity = Vector2()
	if Input.is_action_pressed('ui_right'):
		velocity = Vector2(0, speed).rotated($player.rotation)
		if $player/feet.animation != "walk":
			$player/feet.play("right")
	if Input.is_action_pressed('ui_left'):
		velocity = Vector2(0, -speed).rotated($player.rotation)
		if $player/feet.animation != "walk":
			$player/feet.play("left")
	if Input.is_action_pressed('ui_down'):
		velocity = Vector2(-speed, 0).rotated($player.rotation)
		if $player/feet.animation != "walk":
			$player/feet.play("walk")
	if Input.is_action_pressed('ui_up'):
		velocity = Vector2(speed, 0).rotated($player.rotation)
		if $player/feet.animation != "walk":
			$player/feet.play("walk")
	if Input.is_action_pressed('shoot'):
		$player.play("handgun_shoot")
	else:
		$player.play("handgun_idle")
	if velocity == Vector2():
		$player/feet.play("idle")
	emit_signal("moveplayer",position.x,position.y,$player.rotation)
	velocity = velocity.normalized() * speed

func _physics_process(delta):
	get_input()
	move_and_slide(velocity)
