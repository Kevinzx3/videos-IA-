import React from 'react';
import {
  AbsoluteFill, Audio, Img, OffthreadVideo, Sequence, interpolate, random, spring, staticFile,
  useCurrentFrame, useVideoConfig, Easing,
} from 'remotion';
import type {Datos, Escena, Palabra} from './tipos';

const FUENTE = '"Inter Display", "Inter", system-ui, sans-serif';

// ---------------------------------------------------------------- imagen con movimiento de cámara
const Plano: React.FC<{e: Escena; dur: number}> = ({e, dur}) => {
  const f = useCurrentFrame();
  const p = interpolate(f, [0, dur], [0, 1], {extrapolateRight: 'clamp', easing: Easing.inOut(Easing.quad)});
  let escala = 1.04, x = 0, y = 0;
  switch (e.movimiento ?? 'zoom-in') {
    case 'zoom-in': escala = 1.0 + (e.imagen.endsWith('.mp4') ? 0.04 : 0.09) * p; break;
    case 'zoom-out': escala = 1.12 - 0.09 * p; break;
    case 'pan-izq': escala = 1.12; x = 40 - 80 * p; break;
    case 'pan-der': escala = 1.12; x = -40 + 80 * p; break;
    case 'temblor':
      escala = 1.08 + 0.02 * Math.abs(Math.sin(f / 5));
      x = (random(`x${f}`) - 0.5) * 14; y = (random(`y${f}`) - 0.5) * 14; break;
  }
  // pequeño "golpe" de zoom al entrar en el corte
  const golpe = interpolate(f, [0, 6], [0.04, 0], {extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{overflow: 'hidden', backgroundColor: '#140f22'}}>
      {e.imagen.endsWith('.mp4') ? (
        <OffthreadVideo muted src={staticFile(e.imagen)} style={{
          width: '100%', height: '100%', objectFit: 'cover',
          transform: `translate(${x}px, ${y}px) scale(${escala + golpe})`,
        }}/>
      ) : (
        <Img src={staticFile(e.imagen)} style={{
          width: '100%', height: '100%', objectFit: 'cover',
          transform: `translate(${x}px, ${y}px) scale(${escala + golpe})`,
        }}/>
      )}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- luciérnagas / polvo flotando
const Luciernagas: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      {new Array(28).fill(0).map((_, i) => {
        const x0 = random(`lx${i}`) * 1080, y0 = 500 + random(`ly${i}`) * 1300;
        const v = 10 + random(`lv${i}`) * 25, ph = random(`lp${i}`) * 6.28;
        const yy = y0 - ((v * f) / 30) % 300, xx = x0 + 25 * Math.sin(f / 43 + ph);
        const a = 0.45 + 0.4 * Math.sin(f / 15 + ph);
        return <div key={i} style={{position: 'absolute', left: xx, top: yy, width: 7, height: 7,
          borderRadius: 7, background: '#fffadc', opacity: Math.max(0, a),
          boxShadow: '0 0 12px 4px rgba(255,240,180,0.55)'}}/>;
      })}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- subtítulos estilo referencia
const Subtitulos: React.FC<{palabras: Palabra[]}> = ({palabras}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig(); const t = f / fps;
  const dichas = palabras.filter((p) => p.t0 <= t);
  if (!dichas.length) return null;
  const g = dichas[dichas.length - 1].grupo;
  const grupo = palabras.filter((p) => p.grupo === g);
  if (t > grupo[grupo.length - 1].t1 + 0.4) return null;
  return (
    <AbsoluteFill style={{alignItems: 'center', top: 290, height: 220, padding: '0 80px'}}>
      <div style={{display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '6px 18px',
        fontFamily: FUENTE, fontSize: 58, lineHeight: '78px', color: 'white',
        textShadow: '0 2px 10px rgba(0,0,0,0.45)'}}>
        {grupo.map((p, i) => {
          const actual = p.t0 <= t && t < p.t1, dicha = p.t0 <= t;
          const resaltada = p.clave && dicha;
          return (
            <span key={i} style={{
              fontWeight: actual || p.clave ? 800 : 500,
              opacity: actual || resaltada ? 1 : dicha ? 0.6 : 0,
              padding: resaltada ? '0 12px' : 0, borderRadius: 10,
              background: resaltada ? 'rgba(40,60,120,0.8)' : 'transparent',
              outline: resaltada ? '3px solid #8cb4ff' : 'none',
            }}>{p.texto}</span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- rótulo tipo "300 kg"
const Rotulo: React.FC<{texto: string}> = ({texto}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const k = spring({frame: f - 27, fps, config: {damping: 11, stiffness: 160}});
  if (k <= 0.01) return null;
  return (
    <AbsoluteFill style={{alignItems: 'center', top: 505}}>
      <div style={{transform: `scale(${k})`, fontFamily: FUENTE, fontWeight: 800, fontSize: 66,
        color: '#ffe2aa', background: 'rgba(30,26,30,0.9)', border: '2px solid #5a5046',
        borderRadius: 28, padding: '14px 36px',
        boxShadow: '0 0 40px 10px rgba(255,200,120,0.35)'}}>{texto}</div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- bordes rojos de peligro
const Peligro: React.FC = () => {
  const f = useCurrentFrame();
  const a = 0.45 + 0.25 * Math.sin(f / 4.3);
  return <AbsoluteFill style={{opacity: a, background:
    'radial-gradient(ellipse 70% 60% at 50% 50%, rgba(180,20,20,0) 45%, rgba(180,20,20,0.85) 100%)'}}/>;
};

// ---------------------------------------------------------------- composición
export const Escenas: React.FC<Datos> = ({escenas, palabras, audio}) => {
  const {fps} = useVideoConfig();
  return (
    <AbsoluteFill style={{backgroundColor: '#140f22'}}>
      {escenas.map((e, i) => {
        const from = Math.round(e.ini * fps), dur = Math.max(1, Math.round(e.fin * fps) - from);
        return (
          <Sequence key={i} from={from} durationInFrames={dur}>
            <Plano e={e} dur={dur}/>
            {e.efecto === 'peligro' && <Peligro/>}
            {e.rotulo ? <Rotulo texto={e.rotulo}/> : null}
            {i > 0 && <Fundido/>}
          </Sequence>
        );
      })}
      <Luciernagas/>
      <Subtitulos palabras={palabras}/>
      {audio ? <Audio src={staticFile(audio)}/> : null}
    </AbsoluteFill>
  );
};

const Fundido: React.FC = () => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{background: 'black', opacity: interpolate(f, [0, 3], [0.8, 0], {extrapolateRight: 'clamp'})}}/>;
};
