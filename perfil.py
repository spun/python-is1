import os
import webapp2
import cgi

from google.appengine.ext.webapp import template
import session
from BD.clases import UserDB
from BD.clases import PartidasJugadasDB
from BD.clases import AmigosDB

class Image(webapp2.RequestHandler):
    def get(self):
        usuario = db.get(self.request.get("img_id"))
        if usuario.avatar:
            self.response.headers['Content-Type'] = "img/user"
            self.response.out.write(usuario.avatar)
        else:
           self.response.out.write("No image")
	   
class Perfil(webapp2.RequestHandler):
	def get(self):
		template_values = {}		
		user = None
		userProfile = None
		listaPartidas = None
		listaAmigos = None
		listaPeticiones = None
		isAmigo = False;
		
		self.sess = session.Session('enginesession')
		if self.sess.load():
			user = UserDB().getUserByKey(self.sess.user)
			self.response.out.write("<div><img src='img?img_id=%s'></img>" %user.key())		
			self.response.out.write(' %s</div>' %cgi.escape(user.nick))
			template_values['user'] = user
			userProfile = user
			listaAmigos = AmigosDB().ObtenerAmigos(userProfile)
			listaPeticiones = AmigosDB().ObtenerPeticiones(userProfile)
			if self.request.get('user'):
				if self.request.get('amistad'):
					amigoObjetivo = UserDB().getUserByNick(cgi.escape(self.request.get('user')))
					AmigosDB().PedirAmistad(amigoObjetivo, userProfile)
					self.redirect('/perfil')
				if self.request.get('aceptar'):
					amigo = UserDB().getUserByNick(cgi.escape(self.request.get('aceptar')))
					AmigosDB().AceptarAmistad(user, amigo)
					self.redirect('/perfil')
				if self.request.get('denegar'):
					amigo = UserDB().getUserByNick(cgi.escape(self.request.get('denegar')))
					AmigosDB().DenegarAmistad(user, amigo)
					self.redirect('/perfil')
				if self.request.get('eliminar'):
					amigo = UserDB().getUserByNick(cgi.escape(self.request.get('eliminar')))
					AmigosDB().EliminarAmistad(user, amigo)
					self.redirect('/perfil')
		
		if self.request.get('user'):
			userProfile = UserDB().getUserByNick(cgi.escape(self.request.get('user')))
			if self.sess.load():
				isAmigo = AmigosDB().isAmigo(user, self.request.get('user'))
		
		listaPartidas = PartidasJugadasDB().ObtenerLista(userProfile)	
		if userProfile:
			template_values['userSession'] = user
			template_values['userProfile'] = userProfile
			template_values['listaPartidas'] = listaPartidas
			template_values['listaAmigos'] = listaAmigos
			template_values['listaPeticiones'] = listaPeticiones
			template_values['isAmigo'] = isAmigo
			path = os.path.join(os.path.dirname(__file__), 'perfil.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect('/')

	def post(self):	
		self.response.out.write(cgi.escape(self.request.get('photo')));
		template_values = {}		
		
		self.sess = session.Session('enginesession')
		if self.sess.load():
			userSesion = UserDB().getUserByKey(self.sess.user)
			user = UserDB().getUserByNick(self.request.get('user'))
		
			if user:
				if user.nick == userSesion.nick:
					mail = UserDB().getUserByMail(cgi.escape(self.request.get('mail')))		
					if mail:
						if mail.email == userSesion.email:
							userSesion.nick = self.request.get('user');
							userSesion.password = self.request.get('contra');
							userSesion.email = self.request.get('mail');
							avatar = str(self.request.get('img')) 
							userSesion.avatar = db.Blob(avatar)								
							userSesion.put();
							self.redirect('/perfil');						
						else:
							template_values['errorMsg'] = {
								"title": "Ocurri? un error al modificar el usuario.",
								"text": "La direcci?n de correo electr?nico est? siendo utilizada por otro usuario."
							}
							#Habr?a que pasar el error, pero se sale de la sesi?n
							self.redirect('/perfil');
					else:
						userSesion.nick = self.request.get('user');
						userSesion.password = self.request.get('contra');
						userSesion.email = self.request.get('mail');
						avatar = str(self.request.get('img')) 
						userSesion.avatar = db.Blob(avatar)							
						userSesion.put();
						self.redirect('/perfil');	
				else:
					template_values['errorMsg'] = {
						"title": "Ocurri? un error al modificar el usuario.",
						"text": "El nick est? siendo utilizado por otro usuario."
					}
					#Habr?a que pasar el error, pero se sale de la sesi?n					
					self.redirect('/perfil');
			else:
				usermail = UserDB().getUserByMail(cgi.escape(self.request.get('mail')))		
				if usermail:
					if usermail.email == userSesion.email:
						nick = UserDB().getUserByNick(self.request.get('user'))
						if nick:
							if nick.nick == userSesion.nick:
								userSesion.nick = self.request.get('user');
								userSesion.password = self.request.get('contra');
								userSesion.email = self.request.get('mail');
								avatar = str(self.request.get('img')) 
								userSesion.avatar = db.Blob(avatar)									
								userSesion.put();
								self.redirect('/perfil');						
							else:
								template_values['errorMsg'] = {
									"title": "Ocurri? un error al modificar el usuario.",
									"text": "El nick est? siendo utilizado por otro usuario."
								}
								#Habr?a que pasar el error, pero se sale de la sesi?n							
								self.redirect('/perfil');
						else:
							userSesion.nick = self.request.get('user');
							userSesion.password = self.request.get('contra');
							userSesion.email = self.request.get('mail');
							avatar = str(self.request.get('img')) 
							userSesion.avatar = db.Blob(avatar)							
							userSesion.put();
							self.redirect('/perfil');									
					else:
						template_values['errorMsg'] = {
							"title": "Ocurri? un error al modificar el usuario.",
							"text": "La direcci?n de correo electr?nico est? siendo utilizada por otro usuario."
						}
						#Habr?a que pasar el error, pero se sale de la sesi?n						
						self.redirect('/perfil');
				else:
					userSesion.nick = self.request.get('user');
					userSesion.password = self.request.get('contra');
					userSesion.email = self.request.get('mail');
					avatar = self.request.str_POST['img']
					userSesion.avatar = db.Blob(avatar)					
					userSesion.put();
					self.redirect('/perfil');

		path = os.path.join(os.path.dirname(__file__), 'perfil.html')
		self.response.out.write(template.render(path, template_values))					
app = webapp2.WSGIApplication([('/perfil', Perfil),
			('/img/user', Image)],
                              debug=True)		