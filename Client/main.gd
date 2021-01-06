extends Node

var Player = preload("res://Character.tscn")
var otherPlayers = preload("res://otherPlayers.tscn")
var player = null
# The URL we will connect to
export var websocket_url = "ws://127.0.0.1:6789"
var playerID = null
var players = []

# Our WebSocketClient instance
var _client = WebSocketClient.new()

func _ready():
	player = Player.instance()
	add_child(player)
	_client.connect("connection_closed", self, "_closed")
	_client.connect("connection_error", self, "_closed")
	_client.connect("connection_established", self, "_connected")
	_client.connect("data_received", self, "_on_data")
	player.connect("keyPress", self, "KeyPressed")
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
	if data["type"] == "join":
		print("Joined with ID" + data["ID"])
		playerID = data["ID"]
	if data["type"] == "new_user":
		players.append(otherPlayers.instance())
		add_child(players[-1])

func _process(delta):
	_client.poll()

func KeyPressed(key):
	if playerID != null:
		var data = JSON.print({"action":"move","key":key,"pID":playerID}).to_utf8()
		_client.get_peer(1).put_packet(data)
