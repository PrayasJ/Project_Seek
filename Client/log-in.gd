extends Node

signal login(user,passw)
func hide():
	$Sprite.hide()
func _ready():
	pass
	
func _on_REGISTER_pressed():
	OS.shell_open("http://localhost:9898/authentication")


func _on_LOGIN_pressed():
	emit_signal("login",$Sprite/Sprite/username.text,$Sprite/Sprite/password.text)
