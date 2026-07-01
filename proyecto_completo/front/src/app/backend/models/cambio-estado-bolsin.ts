import { Estado } from './estado';

/** Registro del cambio de estado en el ciclo de vida de un bolsín */
export class CambioEstadoBolsin {
  constructor(
    public fechaHoraInicio: Date,
    public fechaHoraFin: Date | null,
    public estado: Estado,
  ) {}
  
/** Retorna el estado asociado a este cambio */
  getEstado(): Estado {
    return this.estado;
  }
/** Verdadero si es el estado vigente */
  sosActual(): boolean {
    return this.fechaHoraFin === null;
  }
/** Verdadero si el estado es "Enviado" y está vigente */
  sosEnviado(): boolean {
    return this.estado.esEnviado() && this.sosActual();
  }
}
