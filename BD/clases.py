from google.appengine.ext import db
import datetime
import uuid
import random

########### "TABLAS" ##############

class User(db.Model):
	nick = db.StringProperty()
	password = db.StringProperty()
	email = db.EmailProperty()
	idSala = db.StringProperty()
	ptos = db.IntegerProperty(default=0)
	ptosPartida = db.IntegerProperty(default=0)
	avatar = db.BlobProperty()
	
class Sala(db.Model):
	#autor = db.ReferenceProperty(User)
	nombre = db.StringProperty()
	autor = db.StringProperty()
	fechaCrea = db.DateTimeProperty()
	estado = db.StringProperty()
	idSala = db.StringProperty()
	players = db.StringProperty()
	numPlayers = db.StringProperty()
	tipo = db.StringProperty()
	numPuntos = db.IntegerProperty(default=150)
	password = db.StringProperty()
	tematica = db.StringProperty()
	
	
class PartidasJugadas(db.Model):
	user = db.ReferenceProperty(User)
	nombrePartida = db.StringProperty()
	ptos = db.IntegerProperty(default=0)
	win = db.BooleanProperty()

class Palabras(db.Model):
	palabra = db.StringProperty()
	tema = db.StringProperty()
	
class Game(db.Model):
	fechaCrea = db.DateTimeProperty()
	idSala = db.StringProperty()
	palabra = db.ReferenceProperty(Palabras)
	dibujante = db.ReferenceProperty(User)
	rondas = db.IntegerProperty(default=0)
	timestamp = db.DateTimeProperty(default = datetime.datetime.now())
	
class UsersInGame(db.Model):
	game = db.ReferenceProperty(Game)
	user = db.ReferenceProperty(User)
	ptos = db.IntegerProperty(default=0)
	state = db.StringProperty(default="espera")
	
class Amigos(db.Model):
	user = db.StringProperty()
	amigo = db.ReferenceProperty(User)
	aceptado = db.BooleanProperty(default = False)

class Mensaje(db.Model):
	emisor = db.StringProperty()
	receptor = db.StringProperty()
	mensaje = db.StringProperty()
	visto = db.BooleanProperty(default = False)

class Noticia(db.Model):
	titular = db.StringProperty()
	cuerpo = db.TextProperty()
	fechahora= db.DateTimeProperty(default = datetime.datetime.now())
	
class Logros(db.Model):
	nombre = db.StringProperty()
	descripcion = db.TextProperty()
	imagen = db.StringProperty() 
	
class LogrosConseguidos(db.Model):
	logro = db.ReferenceProperty(Logros)
	usuario = db.ReferenceProperty(User)
	mostrado = db.BooleanProperty(default = False)
	fechahora= db.DateTimeProperty(default = datetime.datetime.now())
	
########### METODOS ################

class UserDB:

	""" Anade un nuevo usuario a la base de datos.
		Recibe nick, contrasena y correo
		Devuelve 0 si todo es correcto """
	def AddUser(self, nickName, passwrd, correo):
		nuevoUsuario = User()
		nuevoUsuario.nick = nickName;
		nuevoUsuario.password = passwrd;
		nuevoUsuario.email = correo;
		nuevoUsuario.idSala = "None"
		return nuevoUsuario.put();

	def getUserByNick(self, nickName):
		# Modo 1 (Preferido)
		q = User.all()
		q.filter("nick =", nickName)

		# Modo 2
		# q = db.GqlQuery("SELECT * FROM User WHERE nick = :1 ", nickName)

		results = q.get()
		return results

	def getUserByMail(self, email):
		q = User.all()
		q.filter("email =", email)

		results = q.get()		
		return results
		
	def getUsersQuery(self, nickName, passw):
		q = User.all()
		q.filter("nick =", nickName)
		q.filter("password =", passw)
		
		return q
		
	def getUserByKey(self, key):
		return User.get(key)
	
	def getUsersBySala(self, idSala):
		q = User.all()
		q.filter("idSala =", idSala)
		return q
	
	def userExistsInSala(self, idSala, nick):
		q = User.all()
		q.filter("nick =", nick)
		q.filter("idSala =", idSala)
		res = q.count()
		if res>0:
			return True
		else:
			return False		

	def getNumUsersBySala(self, idSala):
		q = User.all()
		q.filter("idSala =", idSala)
		res = q.count()		
		return res
	
	def getAll(self):
		q = User.all()
		return q


class SalasDB:

	def AddSala(self, nombreSala, autor, tipo, puntos, password, tematica, players):
		u = uuid.uuid4()
		nuevaSala = Sala()
		#nuevaSala.autor = usuario
		nuevaSala.nombre = nombreSala
		nuevaSala.autor = autor
		nuevaSala.fechaCrea = datetime.datetime.now()
		nuevaSala.estado = "Privado"
		nuevaSala.idSala = u.hex
		nuevaSala.tipo = tipo
		nuevaSala.numPuntos = puntos
		nuevaSala.password = password
		nuevaSala.tematica = tematica
		nuevaSala.numPlayers = players
		nuevaSala.put()

	def ListarSalas(self):
		sala=Sala.all()
		res=sala.fetch(100)
		return res
	
	def ListarBusqueda(self, param, texto):
		sala=Sala.all()
		sala.filter(param+" =", texto)
		res=sala.fetch(100)
		return res

	def getSalaByAutor(self, autor):
		sala = Sala.all()
		sala.filter("autor =", autor)
		res = sala.fetch(1)
		return res
		
	def getNumSalas(self):
		sala = Sala.all()
		res = sala.count()
		return res
	
	def deleteSala(self, idSala):
		sala = Sala.all()
		sala.filter("idSala =", idSala)
		res = sala.get()
		Sala.delete(res)
	
	def getSalaById(self, idSala):
		sala = Sala.all()
		sala.filter("idSala =", idSala)
		res = sala.get()
		return res
		
class GameDB:
	
	def AddGame(self, idSala, user):
		newGame = Game()
		newGame.fechaCrea = datetime.datetime.now()
		newGame.idSala = idSala
		newGame.dibujante = user.key()
		
		palabra = None
		p = Palabras.all()
		if p.count() != 0:
			n = random.randint(0, p.count()-1)
			listapalabra = Palabras().all()
			palabra = listapalabra.fetch(1,n)[0]
		else:
			nuevapalabra = Palabras()
			nuevapalabra.palabra = "casa"
			nuevapalabra.tema = "casa"
			nuevapalabra.put()
			palabra = nuevapalabra
		
		newGame.palabra = palabra		
		newGame.put()
		return newGame

	def getGameBySala(self, idSala):
		game = Game.all()
		game.filter("idSala =", idSala)
		res = game.get()
		return res
	
	def deleteGame(self, idSala):
		game = Game.all()
		game.filter("idSala =", idSala)
		res = game.get()
		Game.delete(res)

	def getSalaByGame(self, game):
		game = Game.get(game.key())
		res = game.idSala
		return res
	
	def nuevaPalabra(self, game):
		game = Game.get(game.key())
		palabra = None
		p = Palabras.all()
		miSala = SalasDB().getSalaById(game.idSala)
		if miSala.tematica!="Ninguna":
			p.filter("tema =", miSala.tematica)
		
		if p.count() != 0:
			n = random.randint(0, p.count()-1)
			listapalabra = Palabras().all()
			palabra = listapalabra.fetch(1,n)[0]
		else:
			nuevapalabra = Palabras()
			nuevapalabra.palabra = "casa"
			nuevapalabra.tema = "casa"
			nuevapalabra.put()
			palabra = nuevapalabra
		game.palabra = palabra
		game.put()

	def nuevaPalabra2(self):
		palabra = None
		p = Palabras.all()
		if p.count() != 0:
			n = random.randint(0, p.count()-1)
			listapalabra = Palabras().all()
			palabra = listapalabra.fetch(1,n)[0]
		else:
			nuevapalabra = Palabras()
			nuevapalabra.palabra = "casa"
			nuevapalabra.tema = "casa"
			nuevapalabra.put()
			palabra = nuevapalabra
		return palabra.palabra
	
	def cambiaDibujante(self, idSala, user):
		game = Game.all()
		game.filter("idSala =", idSala)
		res = game.get()
		res.dibujante = user;
		res.put()

	def nuevaRonda(self, game):
		game = Game.get(game.key())
		game.rondas += 1;
		game.put()

class UsersInGameDB:
	
	def AddUserInGame(self, user, game):
		inGame = UsersInGame()
		inGame.game = game
		inGame.user = user
		inGame.put()
	
	def UserExist(self, user):
		inGame = UsersInGame.all()
		inGame.filter("user =", user)
		res = inGame.count()
		if res>0:
			return True
		else:
			return False
		
	def deleteUserInGame(self, user):
		inGame = UsersInGame.all()
		inGame.filter("user =", user)
		res = inGame.get()
		UsersInGame.delete(res)
	
	def scoreUp(self, user, ptos):
		inGame = UsersInGame.all()
		inGame.filter("user =", user)
		res = inGame.get()
		res.ptos += ptos
		res.put()
		user.ptos += ptos
		user.put()
		return res.ptos
	
	def scoreReset(self, user):
		inGame = UsersInGame.all()
		inGame.filter("user =", user)
		res = inGame.get()
		res.ptos = 0
		res.put()

	def changeState(self, user, state="jugando"):
		inGame = UsersInGame.all()
		inGame.filter("user =", user)
		res = inGame.get()
		res.state = state
		res.put()

	def usersPlaying(self, game):
		inGame = UsersInGame.all()
		inGame.filter("state =", "jugando")
		inGame.filter("game =", game)
		res = inGame.count()
		return res

	def getPuntos(self, user):
		inGame = UsersInGame.all()
		inGame.filter("user =", user)
		res = inGame.get()
		return res.ptos

class PalabrasDB:

	def AddPalabra(self, nomPalabra, temaPalabra):
		nuevapalabra = Palabras()
		nuevapalabra.palabra = nomPalabra
		nuevapalabra.tema = temaPalabra
		nuevapalabra.put()

	def getPalabra(self, palabra):
		q = Palabras.all()
		q.filter("palabra =", palabra)
		results = q.get()		
		return results
		
	def getTema(self, tema):
		q = Palabras.all()
		q.filter("tema =", tema)
		results = q.get()		
		return results
		
	def getPalabraTema(self, palabra, tema):
		q = Palabras.all()
		q.filter("palabra =", palabra)
		q.filter("tema =", tema)
		results = q.get()
		return results
	
class PartidasJugadasDB:
	
	def  ObtenerLista(self, user):
		q = PartidasJugadas.all()
		q.filter("user =", user)
		q.filter("ptos !=", 0)
		results = q.fetch(20)
		return results
	
	def setPartida(self, user, titulo, ptos, win):
		partida = PartidasJugadas()
		partida.user = user
		partida.nombrePartida = titulo
		partida.ptos = ptos
		partida.win = win
		partida.put()
		
class AmigosDB:
	
	def ObtenerAmigos(self, user):
		q = Amigos.all()
		q.filter("user =", user.nick)
		q.filter("aceptado =", True)
		results = q.fetch(100)
		return results
	
	def ObtenerPeticiones(self, user):
		q = Amigos.all()
		q.filter("user =", user.nick)
		q.filter("aceptado =", False)
		results = q.fetch(100)
		return results
	
	def DenegarAmistad(self, user, amigo):
		q = Amigos.all()
		q.filter("user =", user.nick)
		q.filter("amigo =", amigo)
		res = q.get()
		Amigos.delete(res)
	
	def EliminarAmistad(self, user, amigo):
		q = Amigos.all()
		q.filter("user =", user.nick)
		q.filter("amigo =", amigo)
		res = q.get()
		Amigos.delete(res)
		q = Amigos.all()
		q.filter("user =", amigo.nick)
		q.filter("amigo =", user)
		res = q.get()
		Amigos.delete(res)
		
	def AceptarAmistad(self, user, amigo):
		q = Amigos.all()
		q.filter("user =", user.nick)
		q.filter("amigo =", amigo)
		res = q.get()
		res.aceptado=True
		res.put()
		q = Amigos()
		q.user=amigo.nick
		q.amigo=user
		q.aceptado=True
		q.put()
		
	def PedirAmistad(self, user, amigo):
		a = Amigos()
		a.user=user.nick
		a.amigo=amigo
		a.aceptado=False
		a.put()
	
	def isAmigo(self, user, amigo):
		q = Amigos.all()
		q.filter("user =", amigo)
		q.filter("amigo =", user)
		q.filter("aceptado =", True)
		res = q.count()
		if res>0:
			return True
		else:
			return False

class MensajesDB:
	def Send(self, e, r, m):
		msj = Mensaje()
		msj.emisor = e
		msj.receptor = r
		msj.mensaje = m
		msj.put()
		
	def Get(self):
		return Mensaje.all()

class NoticiasDB:
	def AddNoticia(self, titular, cuerpo):
		noticia = Noticia()
		noticia.titular = titular
		noticia.cuerpo = cuerpo
		noticia.fechahora = datetime.datetime.now()
		noticia.put()
	
	def getNoticias(self):
		q = db.GqlQuery("SELECT * FROM Noticia ORDER BY fechahora DESC LIMIT 3")
		return q
		
class LogrosConseguidosDB:
	def NuevoLogroConseguido(self, keyLogro, usuario):
		l = Logros.get(keyLogro)
		
		if l:
			q = LogrosConseguidos.all()
			q.filter("usuario =", usuario)
			q.filter("logro =", l)		
			res = q.count()
			
			if res == 0:
				logConseguido = LogrosConseguidos()
				logConseguido.usuario = usuario
				logConseguido.logro = l
				logConseguido.put()
