extends Node2D

signal leave()

func elim(id):
	get_node(id+'/dead').show()

func init(t):
	for child in get_children():
		if child.name[0] != 'p': continue
		child.get_child(1).hide()
	$Timer.wait_time = t
	$Timer.start()

func _ready():
	$Timer.stop()

func set_names(id, name):
	if len(name)>8: get_node(id+'/name').text = name.left(8)+'...'
	else: get_node(id+'/name').text = name

func _process(delta):
	$time.text = str(floor($Timer.time_left/60)) + ':'
	if int($Timer.time_left)%60 < 10: $time.text = $time.text + '0'
	$time.text = $time.text + str(int($Timer.time_left)%60)
func _on_settings_pressed():
	$GUI.show()
	#get_tree().paused = true


func _on_GUI_leave():
	emit_signal("leave")
