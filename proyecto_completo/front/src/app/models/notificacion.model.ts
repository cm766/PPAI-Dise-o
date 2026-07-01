"Resultado de la notificación enviada al gerente de CM"
export interface InfoNotificacion {
  emailGcm: string;
  numeroBolsin: number;
  coordenadas: { lat: number; lng: number };
  fechaHora: Date;
}
