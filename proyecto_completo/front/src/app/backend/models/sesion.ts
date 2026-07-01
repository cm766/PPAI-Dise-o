import { Usuario } from './usuario';

export class Sesion {
  constructor(
    public fechaHoraInicio: Date,
    public fechaHoraFin: Date | null,
    private usuario: Usuario,
  ) {}

  buscarUsuarioLog(): Usuario {
    return this.usuario;
  }
}
