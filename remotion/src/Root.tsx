import {Composition} from 'remotion';
import {Escenas} from './Escenas';
import type {Datos} from './tipos';

const FPS = 30;
const vacio: Datos = {id: 'demo', total: 3, audio: '', escenas: [], palabras: []};

export const Root: React.FC = () => (
  <Composition
    id="Escenas"
    component={Escenas}
    width={1080}
    height={1920}
    fps={FPS}
    durationInFrames={FPS * 3}
    defaultProps={vacio}
    calculateMetadata={({props}) => ({durationInFrames: Math.ceil(props.total * FPS)})}
  />
);
