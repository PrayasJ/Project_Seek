extends KinematicBody2D

var id = null
var speed = 150
var velocity = Vector2()
var target = Vector2()

#export var weapons = ["flashlight", "handgun", "knife", "rifle", "shotgun"]
export var weapons = ["handgun", "knife"]
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

func init(ID):
	id = ID
	position.x = 0
	position.y = 0

func move(x,y,rot):
	target = Vector2(x,y)
	$player.rotation = rot

func hit_sfx():
	$sfx.set_stream(hit)

func _physics_process(delta):
	velocity = position.direction_to(target) * speed
	if position.distance_to(target) > 5:
		velocity = move_and_slide(velocity)
		$player/feet.play("walk")
	else:
		$player/feet.play("idle")
