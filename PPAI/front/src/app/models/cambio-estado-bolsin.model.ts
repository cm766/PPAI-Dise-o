"Cambio de estado de bolsín según la respuesta del backend"
export interface CambioEstadoBolsin {
  id: number;
  estado: {
    nombre: string;
  };
  fechaHoraInicio: string;
}
