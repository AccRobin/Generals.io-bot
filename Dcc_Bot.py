from socketIO_client import SocketIO
import sys
import math
import queue
import random

###########

user_id = 'H12mz_sr5'
user_name = '[bot]Dcc_Robin'
custom_game_id = 'test_room1'

##########

playerIndex = None
generals = None
cities = []
map1 = []
generals = []
armies = []
terrain = []

width, height, size = -1, -1, -1

homepos = -1
homedis = []

###########

def on_connect():
	print('connect')
	# sock.emit("set_username", user_id, "[bot]Bcc_Robin")
	sock.emit('join_private', custom_game_id, user_id)
	print('has been ready!')
	s = input()
	while s != 'end':
		if s == '1':
			sock.emit('set_force_start', custom_game_id, True);
			print('Joined custom game at https://bot.generals.io/games/' + custom_game_id);
		elif s == '2':
			room_id = int(input())
			sock.emit('set_custom_team', custom_game_id, room_id)
		s = input()

def on_disconnect():
	print('disconnect')

def on_reconnect():
	print('reconnect')
	
def patch(old, diff):
	# print("bliiib", old, diff)
	out=[]
	i=0
	while i < len(diff):
		if(diff[i]):
			out+=old[len(out):len(out)+diff[i]]
		i+=1
		if(i<len(diff) and diff[i]):
			out+=diff[i+1:i+1+diff[i]]
			i+=diff[i]
		i+=1
	# print(out)
	return out

def printg(G) :
	global height, width
	for i in range(height) :
		for j in range(width) :
			print(G[i * width + j], end = ' ')
		print('\n')
	print('\n')

def get_homedis() :
	global homepos, width, height, size, playerIndex
	global terrain
	
	printg(terrain)
	
	for i in range(0, height) :
		for j in range(0, width) :
			if terrain[i * width + j] == playerIndex:
				homepos = i * width + j
				homex, homey = i, j
				
	global homedis
	homedis = [-1 for i in range (size)]
	homedis[homepos] = 0
	
	q = queue.Queue()
	q.put(homepos)
	dx = [0, 1, 0, -1]
	dy = [1, 0, -1, 0]
	while q.empty() == False:
		curpos = q.get()
		# print(curpos, ' ', homedis[curpos])
		x = math.floor(curpos / width)
		y = curpos % width
		for i in range(4):
			xx, yy = x + dx[i], y + dy[i]
			nxtpos = xx * width + yy
			if xx >= 0 and xx < height and yy >= 0 and yy < width :
				if terrain[nxtpos] != -2 and terrain[nxtpos] != -4 and homedis[nxtpos] == -1 :
					homedis[nxtpos] = homedis[curpos] + 1
					q.put(nxtpos)
	
	printg(homedis)
	
def on_game_start(*data):
	global playerIndex
	playerIndex=data[0]['playerIndex']
	replay_url = 'http://bot.generals.io/replays/' +data[0]['replay_id']
	print('Game starting! The replay will be available after the game at ' + replay_url)

has_start = 0

def on_game_update(*data):
	global has_start, width, height, size
	global map1, cities, generals, armies, terrain
	
	if has_start == 0:
		map1 = patch(map1, data[0]['map_diff'])
		width, height = map1[0], map1[1]
		size = width * height

		cities = patch(cities, data[0]['cities_diff'])
		map1 = patch(map1, data[0]['map_diff'])
		generals = data[0]['generals']		
		armies = map1[2 : size + 1]
		terrain = map1[-size: ]
		
		get_homedis()
		has_start = 1

	cities = patch(cities, data[0]['cities_diff'])
	map1 = patch(map1, data[0]['map_diff'])
	generals = data[0]['generals']
	armies = map1[2 : size + 1]
	terrain = map1[-size: ]
	
	global homedis, playerIndex
	
	dx = [0, 1, 0, -1]
	dy = [1, 0, -1, 0]
	
	while True:
		# liste = [i for i,x in enumerate(terrain) if x==playerIndex]
		curpos = random.choice([i for i,x in enumerate(terrain) if x==playerIndex])
		
		x = math.floor(curpos / width)
		y = curpos % width
		i = random.randint(0, 3)
		xx, yy = x + dx[i], y + dy[i]
		nxtpos = xx * width + yy
		if xx >= 0 and xx < height and yy >= 0 and yy < width :
			if terrain[nxtpos] != -2 and homedis[nxtpos] >= homedis[curpos] :
				sock.emit("attack", curpos, nxtpos)
				break
			elif nxtpos in cities :
				sock.emit("attack", curpos, nxtpos)

def leaveGame(*data):
	sock.emit("leave_game")
	sys.exit(0)

sock = SocketIO('https://bot.generals.io')

sock.on('connect', on_connect)
sock.on('disconnect', on_disconnect)
sock.on('reconnect', on_reconnect)
sock.on('game_start', on_game_start)
sock.on('game_update', on_game_update)
sock.on('game_lost', leaveGame)
sock.on('game_won', leaveGame)

TILE_EMPTY = -1
TILE_MOUNTAIN = -2
TILE_FOG = -3
TILE_FOG_OBSTACLE = -4

sock.wait()
print("hello world")