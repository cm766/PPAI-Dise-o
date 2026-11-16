# PATRÓN GRASP APLICADO GENERAL: Experto en Información

from time import timezone

from django.db import models
from django.contrib.auth.models import User

class Usuario(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="perfil"
    )
    empleado = models.ForeignKey('Empleado', on_delete=models.CASCADE, related_name='usuarios')
    
    class Meta:
        db_table = 'Usuario' # Nombre de la tabla en la base de datos
        ordering = ['user__username']  # Ordenar por nombre de usuario de forma predeterminada

    def __str__(self):
        return self.user.username
    # GRASP: Experto en Información
    def obtenerEmpleado(self):  
        return self.empleado  # Retorna el empleado asociado al usuario

class ComisionMedica(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.IntegerField(unique=True)
    direccion = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20)
    #localidad = models.ForeignKey(Localidad, on_delete=models.CASCADE, related_name='comisiones_medicas')

    class Meta:
        db_table = 'ComisionMedica'
        ordering = ['nombre']
        verbose_name_plural = "Comisiones Medicas"

    def __str__(self):
        return self.nombre

    def getNombre(self):
        return self.nombre  # Retorna el nombre de la comisión médica

    def getCodigo(self):
        return str(self.codigo)  # Retorna el código de la comisión médica (los GPS Tracker lo piden como String)
    
class Rol(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(max_length=500, null=True, blank=True) 

    class Meta:
        db_table = 'Rol'
        ordering = ['nombre']
        verbose_name_plural = "Roles"

    def __str__(self):
        return self.nombre
        
    def esGerente(self):
        return self.nombre.upper() == "Gerente".upper()  # Retorna True si el nombre del rol es "Gerente", ignorando mayúsculas y minúsculas

class Estado(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(max_length=500, null=True, blank=True) 
    ambito = models.CharField(max_length=100, choices=[('Bolsin', 'Bolsin')])  # Ambito segun vista estica del CU36 solo puede ser "Bolsin" , para todo el sistema deberian estar las otras opciones

    class Meta:
        db_table = 'Estado'
        ordering = ['nombre']
        verbose_name_plural = "Estados"

    def __str__(self):
        return self.nombre
    
    def esEnviado(self):
        return self.nombre.upper() == "Enviado".upper()  # Retorna True si el nombre del estado es "Enviado", ignorando mayúsculas y minúsculas

class Empleado(models.Model):
    apellido = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    
    rol = models.ForeignKey(
        Rol,
        on_delete=models.CASCADE,
        related_name='empleados'
    )

    asignadoA = models.ForeignKey(
        ComisionMedica,
        on_delete=models.CASCADE,
        related_name='empleados', 
        null=True, blank=True  # Permitir nulo y en blanco para que pueda ser asignado posteriormente
    )
    

    class Meta:
        db_table = 'Empleado'
        ordering = ['apellido', 'nombre']
        verbose_name_plural = "Empleados"
    
    def __str__(self):
        return f"{self.apellido}, {self.nombre}"
        
    def getCM(self):
        return self.asignadoA  # Retorna la comision medica asignada
    
    def esTuCM(self, cm):
        return self.asignadoA == cm  # Retorna True si la comision medica asignada == cm

    def getEmail(self):
        return self.email  # Retorna el email
# GRASP: Polimorfismo / Bajo Acoplamiento
    def sosGerenteCM(self):
        return self.rol.esGerente()  # Retorna True si el rol es "Gerente"
    

class CambioEstadoBolsin(models.Model):
    fechaHoraFin = models.DateTimeField(null=True, blank=True)
    fechaHoraInicio = models.DateTimeField(auto_now_add=True)    
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE, related_name='cambios_estado_bolsin')
    #responsableCE = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='cambios_estado_bolsin')  # confirmar info
    #bolsin = models.ForeignKey('Bolsin', on_delete=models.CASCADE, related_name='cambios_estado_bolsin')

    class Meta:
        db_table = 'CambioEstadoBolsin'
        ordering = ['fechaHoraInicio']
        verbose_name_plural = "Cambios de Estado de Bolsines"

    def __str__(self):
        return f"{self.bolsin} - {self.fechaHoraInicio} -> {self.estado}"

    def getEstado(self):
        return self.estado  # Retorna el estado

    def sosActual(self):
        return self.fechaHoraFin is None  # Retorna True si no hay fechaFin (es actual), 
# GRASP: Bajo Acoplamiento
    def sosEnviado(self):
        return self.estado.esEnviado()  # Retorna True si el nombre del estado es 'Enviado'

class Bolsin(models.Model):
    numeroPrecinto = models.IntegerField(unique=True, null=True, blank=True)  # Permitir nulo y en blanco para que pueda ser asignado posteriormente
    peso = models.FloatField()
    fecha = models.DateField(auto_now_add=True)  # confirmar si la fecha es la fecha de creacion del bolsin
    numeroBolsin = models.IntegerField(unique=True)  
    origen = models.ForeignKey('ComisionMedica', on_delete=models.CASCADE, related_name='bolsines_origen') 
    destino = models.ForeignKey('ComisionMedica', on_delete=models.CASCADE, related_name='bolsines_destino') 
    cambioEstado = models.ForeignKey(CambioEstadoBolsin, on_delete=models.CASCADE, related_name='bolsines_estado')
    # Modelo del GPS Tracker del bolsín (RNF 6). En el análisis era el atributo "modelo" de «interfaz» GPSTracker.
    MODELOS_TRACKER = [
        ('XTR4500L', 'XTR-4500L'),
        ('NavTrackQX7A', 'NavTrack QX-7A'),
        ('GeoPulseMTR900', 'GeoPulse MTR-900'),
    ]
    modeloTracker = models.CharField(max_length=30, choices=MODELOS_TRACKER, default='XTR4500L')

    class Meta:
        db_table = 'Bolsin'
        ordering = ['fecha', 'numeroBolsin']
        verbose_name_plural = "Bolsines"
    
    def sosEnviado(self):  # Confirmar que valor de retorno se quiere, por ahora se devuelve lo que devuelve la funcion sosEnviado() del cambio de estado actual del bolsín
        return self.cambioEstado.sosEnviado()  # Retorna el valor de la función sosEnviado() del cambio de estado actual del bolsín

    def esTuCMOrigen(self, cm):
        return self.origen.getNombre() == cm  # Retorna True o False

    def getNumeroBolsin(self):
        return self.numeroBolsin  # Retorna el número del bolsín

    def getModeloTracker(self):
        return self.modeloTracker  # Retorna el modelo de GPS Tracker del bolsín

    def getCMOrigen(self):
        return self.origen  # Retorna la cm de origen
    
    def modificarBolsin(self, peso):  # En caso de que mas cosas se tengan que mopdificar, se agregan como parametros y se modifican en el metodo
        if self.numeroPrecinto is None :  # Con la condicion de que el numero de precinto sea None, significa que el bolsín no ha sido cerrado y se puede modificar
            self.peso = peso  # Se modifica el peso del bolsín
            self.save()  # Se guarda el cambio en la base de datos
        else:
            raise ValueError("El bolsín esta cerrado y no se puede modificar.")  # En caso de que se tenga que devolver otra cosa se cambia aqui, pero por ahora se devuelve un error

    def darDeBaja(self): #Revisar que se hace, se borra de la base de datos, se cambia el estado a dado de baja, o se hace otra cosa. Por ahora se borra de la base de datos
        if not self.sosEnviado():  # Si el bolsín no ha sido enviado, se elimina de la base de datos
            self.delete()  # Se elimina el registro del bolsín de la base de datos
        else:
            raise ValueError("El bolsín ya fue enviado y no se puede dar de baja.")  # En caso de que se tenga que devolver otra cosa se cambia aqui, pero por ahora se devuelve un error
# GRASP: Creador (Creator)
    def cerrar(self, numeroPrecinto):
        if self.numeroPrecinto is None:  # Si el bolsín no tiene número de precinto, significa que no ha sido cerrado
            self.numeroPrecinto = numeroPrecinto  # Se asigna el número de precinto al bolsín
            self.cambioEstado.fechaHoraFin = timezone.now()  # Se marca la fecha y hora de cierre del cambio de estado actual
            self.cambioEstado.save()  # Se guarda el cambio de estado actualizado en la base de datos
            self.cambioEstado = CambioEstadoBolsin.objects.create(  # Se crea un nuevo cambio de estado para el bolsín con el estado "Cerrado"
                estado=Estado.objects.get(nombre="Cerrado"),  # Se asigna el estado "Cerrado" al nuevo cambio de estado del bolsín  # Consultar si los nombres de los estados se ponen con mayusculas o minusculas
            )
            self.save()  # Se guarda el cambio en la base de datos
        else:
            raise ValueError("El bolsín ya fue cerrado y no se puede cerrar nuevamente.")  # En caso de que se tenga que devolver otra cosa se cambia aqui, pero por ahora se devuelve un error
   # GRASP: Creador         
    def abrirBolsin(self):
        if self.cambioEstado.estado.nombre == "Cerrado":  # Si el bolsín está cerrado, se puede abrir
            self.cambioEstado.fechaHoraFin = timezone.now()  # Se marca la fecha y hora de apertura del cambio de estado actual
            self.cambioEstado.save()  # Se guarda el cambio de estado actualizado en la base de datos
            self.cambioEstado = CambioEstadoBolsin.objects.create(  # Se crea un nuevo cambio de estado para el bolsín con el estado "Abierto"
                estado=Estado.objects.get(nombre="Creado"),  # Se asigna el estado "Creado" al nuevo cambio de estado del bolsín
            )
            self.numeroPrecinto = None  # Se elimina el número de precinto del bolsín al abrirlo
            self.save()  # Se guarda el cambio en la base de datos
        else:
            raise ValueError("El bolsín no está cerrado y no se puede abrir.")  # En caso de que se tenga que devolver otra cosa se cambia aqui, pero por ahora se devuelve un error
    
    def retirarBolsin(self):
        if self.cambioEstado.estado.nombre == "Cerrado":  # Si el bolsín está cerrado, se puede retirar
            self.cambioEstado.fechaHoraFin = timezone.now()  # Se marca la fecha y hora de retiro del cambio de estado actual
            self.cambioEstado.save()  # Se guarda el cambio de estado actualizado en la base de datos
            self.cambioEstado = CambioEstadoBolsin.objects.create(  # Se crea un nuevo cambio de estado para el bolsín con el estado "Retirado"
                estado=Estado.objects.get(nombre="Enviado"),  # Se asigna el estado "Enviado" al nuevo cambio de estado del bolsín
            )
            self.save()  # Se guarda el cambio en la base de datos
            # Implementar la logica de cambios de estados de los remitos asociados al bolsín, si es necesario
   
    def recibirBolsin(self):  # Consultar si se hace algo, por ahora no se hace nada
        # Segun el caso de uso, solo el remito y la documentacion asociada al bolsín se reciben, el bolsín en si no se recibe, por lo que no se hace nada en este metodo
        pass

    def getCMDestino(self):  # Inconsistencia en Vista dinamica y vista estatica CU36 n29
        return self.destino  # Retorna la cm de destino


    def __str__(self):
        return f"Bolsin {self.numeroBolsin} - {self.fecha}"

class Sesion(models.Model):
    
    fechaHoraInicio = models.DateTimeField(auto_now_add=True)
    fechaHoraFin = models.DateTimeField(null=True, blank=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='sesiones')

    class Meta:
        db_table = 'Sesion'
        ordering = ['fechaHoraInicio']
        verbose_name_plural = "Sesiones"

    def __str__(self):
        return f"Sesion de {self.usuario.username} - {self.fechaHoraInicio}"
    
    def buscarUsuarioLog(self):
        return self.usuario  # Retorna el usuario logeado
