export type Escena = {
  imagen: string;          // ruta dentro de public/
  ini: number;             // segundos
  fin: number;
  movimiento?: 'zoom-in' | 'zoom-out' | 'pan-izq' | 'pan-der' | 'temblor';
  rotulo?: string | null;  // recuadro tipo "300 kg"
  efecto?: 'peligro' | null;
};
export type Palabra = {t0: number; t1: number; texto: string; clave: boolean; grupo: number};
export type Datos = {
  id: string;
  total: number;
  audio: string;
  escenas: Escena[];
  palabras: Palabra[];
};
