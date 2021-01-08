extends KinematicBody2D

export var id = 0
export var speed = 250
export var moving = false
export var dir = Vector2()

var velocity = Vector2()

var reload_count = 0
var attacking = 0


export var weapons = ["flashlight", "handgun", "knife", "rifle", "shotgun"]
export var curr_weapon = 0

signal keyPress(key)
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

func init(ID, x, y):
	position.x = x
	position.y = y
	id = ID

func move(key):
	attacking = false
	velocity = Vector2()
	if key =="right":
		if(moving == false):
			$player.play(weapons[curr_weapon]+"_move")
			$player/feet.play("walk" if speed == 250 else  "run")
			moving = true
		velocity.x += 1
	if key =="left":
		if(moving == false):
			$player.play(weapons[curr_weapon]+"_move")
			$player/feet.play("walk" if speed == 250 else  "run")
			moving = true
		velocity.x -= 1
	if key =="up":
		if(moving == false):
			$player.play(weapons[curr_weapon]+"_move")
			$player/feet.play("walk" if speed == 250 else  "run")
			moving = true
		velocity.y -= 1
	if key =="down":
		if(moving == false):
			$player.play(weapons[curr_weapon]+"_move")
			$player/feet.play("walk" if speed == 250 else  "run")
			moving = true
		velocity.y += 1
	if velocity != Vector2():
		dir = velocity
	$player.rotation= velocity.angle()
	$CollisionShape2D.rotation = velocity.angle()
	$CollisionShape2D.rotation_degrees-=90
	velocity = velocity.normalized() * speed

func get_input():
	if Input.is_action_just_pressed("run"):
		speed = 400
	if Input.is_action_just_released("run"):
		speed = 250
	if Input.is_key_pressed(KEY_1):
		curr_weapon=0
		$player/torch.position.x = 600
		$player/torch.scale.x = 4
		$player/torch.scale.y = -4.5
		$player.play(weapons[curr_weapon]+'_'+$player.animation.split('_', true, 1)[1])
	if Input.is_key_pressed(KEY_2):
		curr_weapon=1
		$player/torch.position.x = 400
		$player/torch.scale.x = 3
		$player/torch.scale.y = -3.5
		$player.play(weapons[curr_weapon]+'_'+$player.animation.split('_', true, 1)[1])
	if Input.is_key_pressed(KEY_3):
		curr_weapon=2
		$player/torch.position.x = 400
		$player/torch.scale.x = 3
		$player/torch.scale.y = -3.5
		$player.play(weapons[curr_weapon]+'_'+$player.animation.split('_', true, 1)[1])
	if Input.is_key_pressed(KEY_4):
		curr_weapon=3
		$player/torch.position.x = 400
		$player/torch.scale.x = 3
		$player/torch.scale.y = -3.5
		$player.play(weapons[curr_weapon]+'_'+$player.animation.split('_', true, 1)[1])
	if Input.is_key_pressed(KEY_5):
		curr_weapon=4
		$player/torch.position.x = 400
		$player/torch.scale.x = 3
		$player/torch.scale.y = -3.5
		$player.play(weapons[curr_weapon]+'_'+$player.animation.split('_', true, 1)[1])
	
	if Input.is_key_pressed(KEY_F):
		$player.play(weapons[curr_weapon]+"_melee")
		if $sfx.playing == false:
			$sfx.set_stream(melee)
			$sfx.play()
		
	if Input.is_action_pressed("shoot") and reload_count == 0 and $player.animation.split('_', true, 1)[0] != 'flashlight'and $player.animation.split('_', true, 1)[0] != 'knife':
		$player.play(weapons[curr_weapon]+"_shoot")
		if curr_weapon == 1:
			$sfx.set_stream(handgun)
		if curr_weapon == 3:
			$sfx.set_stream(rifle)
		if curr_weapon == 4:
			$sfx.set_stream(machinegun)
		$sfx.play()
		$player/muzzle.show()
		attacking = true
	
	if Input.is_key_pressed(KEY_R) and $player.animation.split('_', true, 1)[0] != 'flashlight'and $player.animation.split('_', true, 1)[0] != 'knife':
		if curr_weapon == 1:
			reload_count = 3
		if curr_weapon == 3:
			reload_count = 5
		if curr_weapon == 4:
			reload_count = 10
		
	
func hit_sfx():
	$sfx.set_stream(hit)
	
func _physics_process(delta):
	$player/muzzle.hide()
	if moving == true and speed == 250 and ($walk.playing == false or $walk.get_stream() == run):
		$walk.set_stream(walk)
		$walk.play()
	if moving == true and speed == 400 and ($walk.playing == false or $walk.get_stream() == walk):
		$walk.set_stream(run)
		$walk.play()
	if reload_count > 0 and $reload.playing == false:
		$player.play(weapons[curr_weapon]+"_reload")
		$reload.set_stream(reload)
		$reload.play()
		reload_count-=1
	if moving == false and $walk.playing == true:
		$walk.stop()
	if( velocity == Vector2() and moving == true):
		$player.play(weapons[curr_weapon]+"_idle")
		$player/feet.play("idle")
		moving=false
	for i in weapons:
		if $player.animation == i+"_melee" and $player.frame == $player.frames.get_frame_count(i+"_melee")-1 :
			$player.play(weapons[curr_weapon]+"_idle")
			moving=false
		if $player.animation == i+"_shoot" and $player.frame == $player.frames.get_frame_count(i+"_shoot")-1 :
			$player.play(weapons[curr_weapon]+"_idle")
			moving=false
		if $player.animation == i+"_reload" and $player.frame == $player.frames.get_frame_count(i+"_reload")-1 :
			$player.play(weapons[curr_weapon]+"_idle")
			moving=false
	move('none')
	if moving == false and $player.animation.split('_', true, 1)[0] != weapons[curr_weapon]:
		$player.play(weapons[curr_weapon]+'_'+$player.animation.split('_', true, 1)[1])
	$player.rotation= dir.angle()
	$CollisionShape2D.rotation = dir.angle()
	$CollisionShape2D.rotation_degrees-=90
	velocity = move_and_slide(velocity)
