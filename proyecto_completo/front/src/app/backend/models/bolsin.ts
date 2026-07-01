import { CambioEstadoBolsin } from './cambio-estado-bolsin';
import { ComisionMedica } from './comision-medica';

export interface Remito {
  numero: string;
  documentacion: { asunto: string; tipo: string }[];
}

export class Bolsin {
  private cambiosEstado: CambioEstadoBolsin[];

  constructor(
    public numeroBolsin: number,
    public numeroPrecinto: string,
    public peso: number,
    public fecha: Date,
    public cmOrigen: ComisionMedica,
    public cmDestino: ComisionMedica,
    cambiosEstado?: CambioEstadoBolsin[],
    public remitos: Remito[] = [],
    public latitud?: number,
    public longitud?: number,
    public ultimaActualizacion?: Date,
  ) {
    this.cambiosEstado = cambiosEstado ?? [];
  }
/**Verdadero si cambio de estado actual es "Enviado" */
  sosEnviado(): boolean {
    return this.cambiosEstado.some((c) => c.sosEnviado());
  }
/** Verdadero si la CM origen coincide con la indicada */
  esTuCMOrigen(cm: ComisionMedica): boolean {
    return this.cmOrigen.codigo === cm.codigo;
  }
/** Nombre de la CM destino */
  getNumeroBolsin(): number {
    return this.numeroBolsin;
  }

/** Retorna al historial de cambios de estado */
  getCambiosEstado(): CambioEstadoBolsin[] {
    return this.cambiosEstado;
  }

  getCMDestino(): ComisionMedica {
    return this.cmDestino;
  }

  get destino(): string {
    return this.cmDestino.nombre;
  }

  get origen(): string {
    return this.cmOrigen.nombre;
  }

  // Métodos de interfaz
  modificarBolsin(): void {}
  darDeBaja(): void {}
  cerrar(): void {}
  abrirBolsin(): void {}
  retirarBolsin(): void {}
  recibirBolsin(): void {}
}
