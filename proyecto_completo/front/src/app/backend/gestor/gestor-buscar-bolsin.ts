import { Injectable } from '@angular/core';
import { Observable, map } from 'rxjs';
import { Usuario } from '../models/usuario';
import { Empleado } from '../models/empleado';
import { ComisionMedica } from '../models/comision-medica';
import { Bolsin } from '../models/bolsin';
import { CambioEstadoBolsin } from '../models/cambio-estado-bolsin';
import { Estado } from '../models/estado';
import { Rol } from '../models/rol';
import { GpsLocation } from '../models/gps-tracker';
import { BolsinService } from '../../services/bolsin.service';
import { InfoNotificacion } from '../../models/notificacion.model';

@Injectable({ providedIn: 'root' })
export class GestorBuscarBolsin {

  // Atributos
  usuarioLogueado: Usuario | null = null;
  cmOrigenBolsin: ComisionMedica | null = null;
  cmDestinoBolsin: ComisionMedica | null = null;
  confirmacionEnvioCorreo = false;
  bolsinSeleccionado: Bolsin | null = null;
  ubicacionBolsines: Map<number, GpsLocation> = new Map();
  mapa: any = null;
  mapaConBolsines: any = null;

  private bolsines: Bolsin[] = [];

  constructor(private bolsinService: BolsinService) {}

  // Métodos públicos

  // Obtiene todos los bolsines enviados desde el backend a través del servicio HTTP.
  // Construye los objetos de dominio (ComisionMedica, Bolsin, Usuario, etc.) a partir de la respuesta JSON.
  nuevaBusquedaBolsin(): Observable<Usuario> {
    return this.bolsinService.consultarUbicaciones().pipe(
      map((data: any) => {
        this.cmOrigenBolsin = new ComisionMedica('', data.cm, '', '', '');
        const estadoEnviado = new Estado('Enviado', 'Bolsín ha sido enviado', 'Bolsin');
        this.bolsines = (data.bolsines_enviados || []).map((item: any) =>
          this.mapearBolsin(item, estadoEnviado)
        );
        const empleado = new Empleado('', '', '', this.cmOrigenBolsin, new Rol('', ''));
        this.usuarioLogueado = new Usuario(data.cm, empleado);
        return this.usuarioLogueado;
      })
    );
  }

  // Obtiene la Comisión Médica del usuario logueado recorriendo Usuario → Empleado → ComisionMedica.
  buscarCMUsuarioLog(): ComisionMedica {
    if (!this.usuarioLogueado) throw new Error('No hay usuario logueado');
    this.cmOrigenBolsin = this.usuarioLogueado.obtenerEmpleado().getCM();
    return this.cmOrigenBolsin;
  }

  // Filtra la lista de bolsines cargados para devolver solo aquellos con estado "Enviado".
  buscarBolsinesEnviados(): Bolsin[] {
    return this.bolsines.filter((b) => b.sosEnviado());
  }

  // Recorre los bolsines y extrae las coordenadas (latitud/longitud) de cada uno,
  async obtenerUbicaciones(bolsines: Bolsin[]): Promise<{ ubicaciones: Map<number, GpsLocation>; errores: string[] }> {
    const ubicaciones = new Map<number, GpsLocation>();
    const errores: string[] = [];
    bolsines.forEach((b) => {
      if (b.latitud !== undefined && b.longitud !== undefined) {
        ubicaciones.set(b.numeroBolsin, {
          numeroBolsin: b.numeroBolsin,
          latitud: b.latitud,
          longitud: b.longitud,
          fechaHoraUltimoReporte: b.ultimaActualizacion ?? new Date(),
        });
      }
    });
    this.ubicacionBolsines = ubicaciones;
    return { ubicaciones, errores };
  }

  // Dado un bolsín, busca su ubicación en el mapa y devuelve sus coordenadas como string ("lat, lng").
  formatearUbicacion(bolsin: Bolsin): string {
    const loc = this.ubicacionBolsines.get(bolsin.numeroBolsin);
    if (!loc) return '';
    return `${loc.latitud.toFixed(4)}, ${loc.longitud.toFixed(4)}`;
  }

  // Guarda el bolsín seleccionado por el usuario y registra su CM destino.
  tomarSeleccionBolsin(bolsin: Bolsin): void {
    this.bolsinSeleccionado = bolsin;
    this.cmDestinoBolsin = bolsin.cmDestino;
  }

  // Almacena si el usuario confirmó o no el envío del correo de notificación al GCM.
  tomarConfEnvioCorreo(confirmado: boolean): void {
    this.confirmacionEnvioCorreo = confirmado;
  }

  // Obtiene el email del Gerente de la Comisión Médica de destino.
  // Actualmente genera uno por convención de nombre; queda como hook para consulta real al backend.
  buscarEmailGCM(): string {
    return this.cmDestinoBolsin?.nombre
      ? `gcm.${this.cmDestinoBolsin.nombre.toLowerCase().replace(/\s+/g, '')}@example.com`
      : 'gcm@example.com';
  }

  // Envía al backend la solicitud de notificación al GCM con los datos del bolsín seleccionado.
  // Retorna la respuesta del servidor con la información de la notificación enviada.
  llamarCUNotificarUbicacionDeBolsin(): Observable<InfoNotificacion> {
    if (!this.bolsinSeleccionado || !this.cmDestinoBolsin) {
      throw new Error('No hay bolsín seleccionado o CM destino');
    }
    return this.bolsinService.notificarGerentes({
      numero: this.bolsinSeleccionado.numeroBolsin,
      lat: this.bolsinSeleccionado.latitud ?? 0,
      lng: this.bolsinSeleccionado.longitud ?? 0,
      fecha: this.bolsinSeleccionado.ultimaActualizacion ?? new Date(),
    });
  }

  // Limpia el estado interno del gestor al finalizar el caso de uso.
  finCU(): void {
    this.bolsinSeleccionado = null;
    this.confirmacionEnvioCorreo = false;
    this.ubicacionBolsines.clear();
  }

  // Métodos privados

  // Convierte un item del JSON devuelto por el backend en un objeto Bolsin del dominio,
  // creando también su CambioEstadoBolsin y su ComisionMedica de destino.
  private mapearBolsin(item: any, estado: Estado): Bolsin {
    const cmDestino = new ComisionMedica('', item.destino, '', '', '');
    const cambio = new CambioEstadoBolsin(
      new Date(item.fecha || Date.now()),
      null,
      estado,
    );
    const bolsin = new Bolsin(
      item.numeroBolsin,
      item.numeroPrecinto,
      item.peso,
      new Date(item.fecha || Date.now()),
      this.cmOrigenBolsin!,
      cmDestino,
      [cambio],
      [],
      item.latitud,
      item.longitud,
      item.ultimaActualizacion ? new Date(item.ultimaActualizacion) : new Date(),
    );
    return bolsin;
  }
}
