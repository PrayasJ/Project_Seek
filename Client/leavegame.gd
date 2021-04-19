extends Node2D

signal leave()

func _ready():
	pass

func _on_apply_pressed():
	#get_tree().paused = false
	hide()

func _on_yes_bttn_pressed():
	pass

func _on_no_bttn_pressed():
	pass # Replace with function body.

func _on_joypad_pressed():
	pass # Replace with function body.


func _on_leave_pressed():
	emit_signal("leave")
