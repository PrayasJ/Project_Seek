extends KinematicBody2D

var id = null
var speed = 150
var velocity = Vector2()
var username = null
var state = false

export var weapons = {"handgun":false, "knife":false}
signal moveplayer(x,y,vx,vy,rot)
signal shoot(ray)
signal knife(ray)
signal leave()
var target = Vector2()
var melee = load("res://assets/sfx/melee.wav")
var run = load("res://assets/sfx/run.wav")
var walk = load("res://assets/sfx/footstep.wav")
var handgun = load("res://assets/sfx/handgun.wav")
var knife = load("res://assets/sfx/knife.wav")
var hit = load("res://assets/sfx/hit.wav")

func set_names(id,name):
	$base.set_names(id,name)

func init(ID,x,y,user):
	username = user
	if len(user)>8: $username.text = user.left(8)+'...'
	else: $username.text = user
	id = ID
	position.x = x
	position.y = y
	$base.init(300)

func set_type(type):
	weapons[type] = true
	$player.play(type+"_idle")
	$player.connect("animation_finished",$player,"play",[type+'_idle'])

func getID():
	return id

func getpos():
	return position

func getx():
	return position.x

func gety():
	return position.y

#func _input(event):
#	if event.is_action_pressed('scroll_up'):
#		$Camera2D.zoom = $Camera2D.zoom - Vector2(0.1, 0.1)
#	if event.is_action_pressed('scroll_down'):
#		$Camera2D.zoom = $Camera2D.zoom + Vector2(0.1, 0.1)
	
func hit_sfx():
	$sfx.set_stream(hit)

func move(x, y, vx, vy, rot):
	velocity = Vector2(vx,vy)
	$player.rotation = rot
	
func get_input():
	$player.look_at(get_global_mouse_position())
	velocity = Vector2()
	if Input.is_action_pressed('run'):
		speed = 250
	else:
		speed = 150
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
	
	if weapons['handgun']:
		if Input.is_action_just_pressed("shoot"):
			$player.play("handgun_shoot")
			$player/muzzle.show()
			emit_signal("shoot",$RayCast2D.get_collider())
		else:
			$player/muzzle.hide()

	if weapons['knife']:
		if Input.is_action_just_pressed('shoot'):
			$player.play("knife_melee")
			emit_signal("knife",$RayCast2D.get_collider())

	if velocity == Vector2():
		$player/feet.play("idle")
	$CollisionShape2D.rotation_degrees = $player.rotation_degrees - 90
	$RayCast2D.rotation_degrees = $player.rotation_degrees
	velocity = velocity.normalized() * speed
	emit_signal("moveplayer",position.x,position.y,velocity.x,velocity.y,$player.rotation)

func _physics_process(delta):
	get_input()
	move_and_slide(velocity)


func _on_base_leave():
	emit_signal("leave")
