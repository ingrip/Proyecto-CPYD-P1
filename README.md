# Plati-Cats

![Plati-Cats Logo](static/logo.png)

Plati-Cats es un **chat web en tiempo real** que permite a los usuarios comunicarse en **comunidades temáticas** o mediante **chats privados**, con **notificaciones**, sonidos de mensaje y lista dinámica de usuarios activos.

## Guía de inicio

Las siguientes instrucciones ayudarán en la ejecución del proyecto en tú máquina local para propósitos de desarrollo y prueba.

### Pre-requisitos 

- Python 3.8 o superior
- Cuenta de Firebase (para autenticación y base de datos)
- Navegador web moderno (Chrome, Firefox, Edge)


### Tecnologías utilizadas


# Backend
```
Python, Flask, Flask-socketIO
```

# Base de datos
```
Firebase Firestore
```

# Frontend
```
HTML, CSS, JavaScript  
```

# Liberías
```
Socket.IO, Firebase Auth (para login con Google)
```


### Instalacion

Para ejecutar el proyecto, sigue los siguientes pasos:

1. **Clonar el repositorio**
```
git clone https://github.com/ingrip/Proyecto-CPYD-P1.git
cd Proyecto-CPYD-P1
```
2. **Instala las dependencias**

```
pip install -r requirements.txt
```

3. **Coloca tu archivo `firebase_key.json` en la raíz del proyecto.**
* Ve a Firebase Console
* Crea un nuevo proyecto o selecciona uno existente
* Genera una nueva clave privada en Configuración del proyecto → Cuentas de servicio
* Descarga el archivo JSON y renómbralo como firebase_key.json
* Coloca firebase_key.json en la raíz del proyecto

4. **Ejecuta la aplicación:**

```
python app.py
```
5. **Abre el navegador en:**
```
http://localhost:5000
```

## Uso
1. Inicia sesión con tu cuenta de Google.
2. Selecciona una comunidad para chatear.
3. Haz clic en un usuario de la lista para abrir un chat privado.
4. Envía mensajes y recibe notificaciones y sonido al recibir mensajes nuevos.

##  Funcionamiento interno

### Eventos Socket.IO

**Eventos que el cliente envía al servidor:**

| Evento | Descripción |
|--------|-------------|
| `join` | Registrar usuario activo |
| `join_comunidad` | Unirse a una sala de comunidad |
| `mensaje` | Enviar mensaje (público o privado) |
| `cargar_historial` | Solicitar mensajes anteriores |

**Eventos que el servidor envía al cliente:**

| Evento | Descripción |
|--------|-------------|
| `message` | Recibir nuevo mensaje |
| `historial` | Recibir historial de mensajes |
| `usuarios_activos` | Lista actualizada de usuarios |

## Construido con

* [Python](https://www.python.org/) - Backend con Flask y Socket.IO
* [Flask](https://flask.palletsprojects.com/) - Framework web
* [Firebase](https://firebase.google.com/) - Base de datos para mensajes
* [HTML/CSS/JS](https://developer.mozilla.org/) - Frontend
* [Socket.IO](https://socket.io/) - Comunicación en tiempo real


## Autores

* **Ingrid Yuliana Peréz Rpodríguez** - *367760* - [ingrip](https://github.com/ingrip)
* **Hector Rodríguez Loya** - *363325* - []()
* **Luis Arturo Herandez Castillo** - *367685* - []()
* **Jazmin  Cruz González** - *367770* - [JazCrz194](https://github.com/JazminCrz194)
