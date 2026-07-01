// Patrón GRASP aplicado: Alta Cohesión

import { Component, OnInit, inject, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { DatePipe } from '@angular/common';
import { InfoNotificacion } from '../../models/notificacion.model';
import { Usuario } from '../../models/usuario.model';
import { Bolsin } from '../../models/bolsin.model';
import { ServidorMapaLeaflet } from '../../services/servidor-google-map';
import { BolsinService } from '../../services/bolsin.service';
import { GpsLocation } from '../../models/gps-location.model';

type Paso =
	| 'cargando'
	| 'localizando'
	| 'mapa'
	| 'detalleBolsin'
	| 'a3Error'
	| 'emailDialog'
	| 'enviando'
	| 'exito'
	| 'error'
	| 'vacio';

@Component({
	selector: 'app-pantalla-buscar-bolsin',
	standalone: true,
	imports: [FormsModule, DatePipe, RouterLink],
	templateUrl: './pantalla-buscar-bolsin.html',
	styleUrl: './pantalla-buscar-bolsin.css',
})
export class PantallaBuscarBolsin implements OnInit {
	private bolsinService = inject(BolsinService);

	// Atributos (Vista estática)
	mapaBolsines: ServidorMapaLeaflet | null = null;
	bolsinSeleccionado: Bolsin | null = null;
	confirmacionEnvioCorreo = false;
	usuarioLogueado: Usuario | null = null;

	// Atributos de implementación
	paso = signal<Paso>('cargando');
	bolsines: Bolsin[] = [];
	filtrados: Bolsin[] = [];
	destinos: string[] = [];
	ubicaciones: Map<number, GpsLocation> = new Map();
	cmOrigen: string = '';
	filtroPrecinto = '';
	filtrodestino = '';
	infoNotificacion: InfoNotificacion | null = null;
	errorMessage = '';

	private servidorMapa: ServidorMapaLeaflet | null = null;

	// Métodos públicos (Diagrama de clases)

	// Inicia el caso de uso: consulta los bolsines del backend a través del gestor.
	ngOnInit(): void {
		this.opcConsultarUbiBolsin();
		(window as any).seleccionarDesdeLista = (num: number) => {
			this.tomarSeleccionBolsin(num);
		};
	}

	// Punto de entrada del caso de uso: obtiene los bolsines enviados y los muestra en pantalla.
	opcConsultarUbiBolsin(): void {
		this.habilitarVentana();

		this.bolsinService.consultarUbicaciones().subscribe({
			next: (res: any) => {
				// Mapeamos de acuerdo a la estructura limpia que devuelve tu API en Django
				this.usuarioLogueado = res.user || null;
				this.cmOrigen = res.cm || '';
				this.bolsines = res.bolsines_enviados || [];

				this.mostrarCMUsuarioLog();
				this.destinos = [...new Set(this.bolsines.map(b => b.destino))];

				if (this.bolsines.length === 0) {
					this.paso.set('vacio');
				} else {
					this.procesarCoordenadas();
				}
			},
			error: () => {
				this.errorMessage = 'Error al cargar bolsines';
				this.paso.set('error');
			},
		});
	}

	// Prepara la ventana para la consulta, mostrando el estado de carga.
	habilitarVentana(): void {
		this.paso.set('cargando');
	}

	// Muestra el nombre de la Comisión Médica del usuario logueado.
	mostrarCMUsuarioLog(): void {
		// Ya no dependemos de un gestor de backend; usamos la propiedad asignada en la respuesta
		this.cmOrigen = this.cmOrigen || '';
	}

	// Prepara las ubicaciones de cada bolsín y pasa a mostrar el mapa.
	procesarCoordenadas(): void {
		this.paso.set('localizando');

		this.ubicaciones.clear();

		this.bolsines.forEach((b) => {
			if (b.latitud !== undefined && b.longitud !== undefined) {
				this.ubicaciones.set(b.numeroBolsin, {
					numeroBolsin: b.numeroBolsin,
					latitud: b.latitud,
					longitud: b.longitud,
					fechaHoraUltimoReporte: b.ultimaActualizacion ? new Date(b.ultimaActualizacion) : new Date(),
				});
			} else {
				this.ubicaciones.set(b.numeroBolsin, {
					numeroBolsin: b.numeroBolsin,
					latitud: -34.6037,
					longitud: -58.3816,
					fechaHoraUltimoReporte: new Date(),
				});
			}
		});

		this.mostrarBolsinLocation();
	}

	// Renderiza el mapa Leaflet con los marcadores de los bolsines filtrados.
	mostrarBolsinLocation(): void {
		this.paso.set('mapa');

		this.filtrados = this.bolsines.filter((b) => {
			const matchP =
				!this.filtroPrecinto ||
				b.numeroPrecinto.toString().includes(this.filtroPrecinto);
			const matchD =
				!this.filtrodestino ||
				String(b.destino)
					.toLowerCase()
					.includes(this.filtrodestino.toLowerCase());
			return matchP && matchD;
		});

		setTimeout(() => {
			const el = document.getElementById('mapa-bolsines');
			if (!el) return;

			if (!this.servidorMapa) {
				this.servidorMapa = new ServidorMapaLeaflet(
					'mapa-bolsines',
					[-31.4201, -64.1888],
					6,
				);
				this.servidorMapa.getMapa();
			} else {
				this.servidorMapa.limpiarMarcadores();
			}

			this.mapaBolsines = this.servidorMapa;
			const sm = this.servidorMapa!;

			const colores = [
				'#6366f1',
				'#10b981',
				'#f59e0b',
				'#ef4444',
				'#8b5cf6',
				'#ec4899',
			];
			let i = 0;

			this.filtrados.forEach((b) => {
				const loc = this.ubicaciones.get(b.numeroBolsin);
				if (!loc) return;

				const color = colores[i % colores.length];
				i++;

				const popupHtml = `
          <div style="font-family:Inter,sans-serif;font-size:13px;min-width:200px">
            <strong style="color:${color}">Bolsín #${b.numeroBolsin}</strong><br>
            <span style="color:#64748b">Destino:</span> ${b.destino}<br>
            <span style="color:#64748b">Estado:</span> Enviado<br>
            <span style="color:#64748b">Última actualización:</span><br>
            ${loc.fechaHoraUltimoReporte.toLocaleString('es-AR')}<br>
            <button onclick="seleccionarDesdeLista(${b.numeroBolsin})"
              style="margin-top:8px;background:${color};color:#fff;border:none;border-radius:6px;padding:6px 14px;font-size:12px;cursor:pointer">
              Seleccionar bolsín
            </button>
          </div>`;

				const icono = sm.crearIcono(color);
				const marker = sm.agregarMarcador(
					loc.latitud,
					loc.longitud,
					popupHtml,
					icono,
				);
				(marker as any).numeroBolsin = b.numeroBolsin;
			});

			sm.ajustarVista();
			this.mapaBolsines = sm;
			this.pedirSeleccionBolsin();
		}, 0);
	}

	// Expone una función global para que los popups del mapa puedan seleccionar un bolsín.
	pedirSeleccionBolsin(): void {
		(window as any).seleccionarBolsin = (numeroBolsin: number) => {
			const bolsin = this.bolsines.find((b) => b.numeroBolsin === numeroBolsin);
			if (bolsin) {
				this.bolsinSeleccionado = bolsin;
			}
		};
	}

	// Maneja la selección de un bolsín desde la lista o el mapa y delega en procesarSeleccion.
	tomarSeleccionBolsin(num: number): void {
		this.bolsinSeleccionado =
			this.bolsines.find((b) => b.numeroBolsin === num) || null;
		this.procesarSeleccion();
	}

	// Verifica si el bolsín tiene coordenadas; si no, muestra error A3; si sí, muestra detalle.
	procesarSeleccion(): void {
		if (
			this.bolsinSeleccionado &&
			(this.bolsinSeleccionado.latitud === undefined ||
				this.bolsinSeleccionado.longitud === undefined)
		) {
			this.paso.set('a3Error');
		} else {
			this.paso.set('detalleBolsin');
			this.pedirConfirmacionEnvioCorreo();
		}
	}

	// Cambia la pantalla al diálogo de confirmación de envío de correo.
	pedirConfirmacionEnvioCorreo(): void {
		this.paso.set('emailDialog');
	}

	// Procesa la respuesta del usuario sobre el envío del correo: si confirma, envía la notificación.
	tomarConfirmacionEnvioCorreo(conf: boolean): void {
		this.confirmacionEnvioCorreo = conf;

		if (!conf) {
			this.paso.set('detalleBolsin');
			return;
		}

		if (this.bolsinSeleccionado) {
			this.paso.set('enviando');

			this.bolsinService.notificarGerentes({
				numero: this.bolsinSeleccionado.numeroBolsin,
				lat: this.bolsinSeleccionado.latitud,
				lng: this.bolsinSeleccionado.longitud,
				fecha: this.bolsinSeleccionado.ultimaActualizacion
			}).subscribe({
				next: (res: InfoNotificacion) => {
					this.infoNotificacion = res;
					this.mostrarMensajeExito();
				},
				error: () => {
					this.errorMessage = 'Error al enviar';
					this.paso.set('error');
				},
			});
		}
	}

	// Muestra la pantalla de éxito con los datos de la notificación enviada.
	mostrarMensajeExito(): void {
		this.paso.set('exito');
		setTimeout(() => this.servidorMapa?.getMapa()?.invalidateSize(), 100);
	}
}
