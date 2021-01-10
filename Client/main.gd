extends Node

var Player = preload("res://Character.tscn")
var otherPlayers = preload("res://otherPlayers.tscn")
var player = null
# The URL we will connect to
export var websocket_url = "ws://127.0.0.1:6789"
var players = {}
var pID = null
# Our WebSocketClient instance
var _client = WebSocketClient.new()

func _ready():
	_client.connect("connection_closed", self, "_closed")
	_client.connect("connection_error", self, "_closed")
	_client.connect("connection_established", self, "_connected")
	_client.connect("data_received", self, "_on_data")
	var err = _client.connect_to_url(websocket_url)
	if err != OK:
		print("Unable to connect")
		set_process(false)

func _closed(was_clean = false):
	print("Closed, clean: ", was_clean)
	set_process(false)

func _connected(proto = ""):
	var jdat = {'action': 'join'}
	#_client.get_peer(1).put_var(JSON.print(jdat))

func _on_data():
	var data = _client.get_peer(1).get_packet().get_string_from_utf8()
	data = JSON.parse(data).result
	if data["action"] == "sent_pID":
		print("Joined with ID" + data["pID"])
		pID = data["pID"]
	if data["action"] == "new_user":
		players[data['ID']] = otherPlayers.instance()
		players[data['ID']].init(data['ID'], data['x'], data['y'])
		add_child(players[data['ID']])
		print("New User added")
	if data["action"] == "move":
		players[data['pID']].move(data['x'],data['y'],data['rot'])
	if data['action'] == "joined_room":
		players[data['joined_room']] = otherPlayers.instance()
		players[data['joined_room']].init(data['joined_room'])
		add_child(players[data['joined_room']])
	if data['action'] == "in_room":
		players[data['in_room']] = otherPlayers.instance()
		players[data['in_room']].init(data['in_room'])
		add_child(players[data['in_room']])
func _process(delta):
	_client.poll()

func _moveplayer(x,y,rot):
	var playerID = player.getID()
	if playerID != null:
		var data = JSON.print({"action":"move","pID":playerID,'x':x, 'y':y, 'rot':rot}).to_utf8()
		_client.get_peer(1).put_packet(data)


func _on_Play_pressed():
	$Map.show()
	$GUI.hide()
	player = Player.instance()
	add_child(player)
	player.connect("moveplayer", self, "_moveplayer")
	player.init(pID)
	var data = JSON.print({"action":"play","pID":pID,"party":"0",'x':0, 'y':0, 'rot':0}).to_utf8()
	_client.get_peer(1).put_packet(data)
