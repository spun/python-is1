import os
import webapp2
import json

from google.appengine.ext.webapp import template

import session
from BD.clases import SalasDB
from BD.clases import UserDB
from BD.clases import GameDB
from BD.clases import UsersInGameDB
from BD.clases import Palabras
import urllib2

class Salas(webapp2.RequestHandler):
	def get(self):
		miPag = self.request.get('p', default_value='0')
		if miPag == '0':
			self.redirect("/salas?p=1")	
		else:
			template_values = {}
			# Extraemos el usuario de la sesion 
			self.sess = session.Session('enginesession')
			if self.sess.load():
				user = UserDB().getUserByKey(self.sess.user)
				if user:
					template_values['user'] = user
					#Si el usuario ya estaba en una sala lo redirigimos a ella
					if user.idSala!="None":
						self.redirect("/salajuego?id="+str(user.idSala))
				
			
			#Extraemos el numero de paginas que tiene el listado de salas
			numPags=0
			if SalasDB().getNumSalas()/8==0:
				numPags=1
			else:
				numPags=(SalasDB().getNumSalas()/8)+1
				
			salas=SalasDB()		
			
			if self.request.get('salaText') and self.request.get('param') != "Todas":
				parametro = self.request.get('param')
				parametro = parametro.lower()
				parametro = urllib2.unquote(parametro)
				textoBuscar = self.request.get('salaText')
				cadena= urllib2.unquote(textoBuscar)
				res=salas.ListarBusqueda(parametro, cadena)
				numPags=1
			else:
				res=salas.ListarSalas()
			#Listamos las salas que hay por acada pagina
			res2 =[]
			i=0
			if int(self.request.get('p')) <= numPags:
				for sala in res:
					if i>=(int(self.request.get('p'))-1)*8 and i<(int(self.request.get('p')))*8:
						res = UserDB().getUsersBySala(sala.idSala)
						sala.players = str(res.count())
						res2.append(sala)
						sala.put()
					i+=1
			else:
				self.redirect("/salas?p=1")
				
			#Listamos los temas de palabras
			listaT = []
			listaTemas = Palabras.all()
			for tema in listaTemas:
				if tema.tema not in listaT:
					listaT.append(tema.tema)
				
			template_values['salas_list'] = res2
			template_values['temas_list'] = listaT
			template_values['numSalas']=SalasDB().getNumSalas()
			template_values['pags']= numPags
			template_values['pag']=self.request.get('p')
			template_values['nextPage']=int(self.request.get('p'))+2
			template_values['prevPage']=int(self.request.get('p'))-2
			template_values['next']=int(self.request.get('p'))+1
			template_values['prev']=int(self.request.get('p'))-1
			path = os.path.join(os.path.dirname(__file__), 'salas.html')
			self.response.out.write(template.render(path, template_values))
		
	def post(self):
		self.sess = session.Session('enginesession')
		if self.sess.load():
			user = UserDB().getUserByKey(self.sess.user)
			if self.request.get('nombre'): #!="" and SalasDB().getSalaByAutor(user.nick)=="":
				partyPass=None
				tipo=None
				puntos = 0
				numPlayers = 0
				#Creamos una nueva sala	
				salas=SalasDB()			
				nombre=self.request.get('nombre')
				autor=user.nick
				if self.request.get('password'):
					partyPass = self.request.get('password')
				if self.request.get('tipo') == "Puntos":
					tipo = "Puntos"
					puntos = int(self.request.get('puntos'))
				else:
					tipo="Rondas"
					
				tematica = self.request.get('tema')
				numPlayers = self.request.get('players')
				
				salas.AddSala(nombre, autor, tipo, puntos, partyPass, tematica, numPlayers)
				#Insertamos al usuario que creo la sala en esta
				miSala=SalasDB().getSalaByAutor(user.nick)
				user.idSala=miSala[0].idSala
				user.put()
				#Creamos el juego
				game = GameDB()
				miJuego = game.AddGame(user.idSala, user)
				#Metemos al usuario en el juego
				userGame = UsersInGameDB()
				userGame.AddUserInGame(user, miJuego)
				#Redireccionamos al usuario
				self.redirect("/salas?p=1")
			else:
				self.redirect("/salas?p=1")
		else:
			self.redirect("/salas?p=1")


class BuscadorSalas(webapp2.RequestHandler):
	def get(self):
		salas=SalasDB()
		messageRaw={}
		if self.request.get('b'):
			cadena= urllib2.unquote(self.request.get('b'))
			res=salas.ListarBusqueda(cadena)
		else:
			res=salas.ListarSalas()
		
		for r in res:
			messageRaw = {
				"idSala": r.idSala, 
				"content": {
					"nombre": r.nombre,
					"autor": r.autor,
					"fechaCrea": str(r.fechaCrea.hour) + ":" + str(r.fechaCrea.minute),
					"players": r.players,
					"tipo": r.tipo,
					"password": r.password
					}
				}
			
		message = json.dumps(messageRaw)
		self.response.out.write(message)	
		

app = webapp2.WSGIApplication([('/salas', Salas),
					('/busquedasalas', BuscadorSalas)],
				debug=True)
