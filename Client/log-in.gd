extends Node

signal login(user,passw)
func hide():
	$Sprite.hide()
func _ready():
	pass

func incorrect():
	$Sprite/Sprite/incorrect.show()
	yield(get_tree().create_timer(3.0), "timeout")
	$Sprite/Sprite/incorrect.hide()

func _on_REGISTER_pressed():
	OS.shell_open("https://proj-seek.herokuapp.com/authentication")


func _on_LOGIN_pressed():
	emit_signal("login",$Sprite/Sprite/username.text,$Sprite/Sprite/password.text)
