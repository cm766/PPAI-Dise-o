export interface Bolsin {
  id: number;
  numeroBolsin: number;
  numeroPrecinto: string;
  destino: string; 
  origen: string;
  latitud?: number;           
  longitud?: number;          
  ultimaActualizacion?: string; 
  ubicacionDisponible?: boolean; // A3: false si el GPS Tracker no pudo informar la ubicación
}