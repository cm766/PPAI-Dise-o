import { Empleado } from './empleado';

export interface SafeUser {
  id: string;
  nombre: string;
  email: string;
}

export interface UpdateUserRoleDto {
  rol: string;
}

export class Usuario {
  constructor(public user: string, private empleado: Empleado) {}

  obtenerEmpleado(): Empleado {
    return this.empleado;
  }
}
