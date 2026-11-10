import {Config} from '@remotion/cli/config';
import fs from 'fs';

// En la nube usa el Chromium ya instalado; en tu PC Remotion descarga el suyo solo.
const chromium = '/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell';
if (fs.existsSync(chromium)) Config.setBrowserExecutable(chromium);
Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
