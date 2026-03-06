// usar el socket que ya existe en la página
usuario = JSON.parse(localStorage.getItem("usuario"))

const comunidadActual = window.comunidadActual || null
const chatPrivadoActual = window.chatPrivadoActual || null

if (Notification.permission !== "granted") {
    Notification.requestPermission()
}

const sonido = new Audio("/static/sonido.mp3")

socket.on("message", function(data){
    // Solo pedir historial después de conectar
    socket.on("connect", function () {
        socket.emit("cargar_historial", { comunidad: comunidad });
    });
    if (data.uid === usuario.uid) return

    let mostrarNotificacion = false

    if (data.comunidad){
        if (comunidadActual !== data.comunidad){
            mostrarNotificacion = true
        }
    }

    if (data.privado){
        if (chatPrivadoActual !== data.uid){
            mostrarNotificacion = true
        }
    }

    if (mostrarNotificacion){

        sonido.play()

        if (Notification.permission === "granted"){
            new Notification(data.nombre,{
                body: data.mensaje,
                icon: "/static/logo.png"
            })
        }

    }

})