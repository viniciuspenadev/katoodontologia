import path from 'node:path';
import { fileURLToPath } from 'node:url';
import sharp from 'sharp';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const familyPath = path.join(root, 'src/assets/familia-kato-recorte-v2.png');
const logoPath = path.join(root, 'public/brand/kato-logo.svg');
const outputPath = path.join(root, 'public/brand/og-kato-light.jpg');

const width = 1200;
const height = 630;

const background = Buffer.from(`
  <svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
    <defs>
      <linearGradient id="page" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="#ffffff"/>
        <stop offset="0.56" stop-color="#f6fcfc"/>
        <stop offset="1" stop-color="#dff8f8"/>
      </linearGradient>
      <radialGradient id="glow" cx="0" cy="0" r="1" gradientTransform="translate(1030 100) rotate(132) scale(440 390)">
        <stop offset="0" stop-color="#01d4df" stop-opacity="0.26"/>
        <stop offset="0.58" stop-color="#bef5f6" stop-opacity="0.34"/>
        <stop offset="1" stop-color="#bef5f6" stop-opacity="0"/>
      </radialGradient>
      <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0" stop-color="#00c9d4"/>
        <stop offset="1" stop-color="#079a9c"/>
      </linearGradient>
      <filter id="shadow" x="-20%" y="-20%" width="140%" height="150%">
        <feDropShadow dx="0" dy="20" stdDeviation="26" flood-color="#103a3d" flood-opacity="0.10"/>
      </filter>
    </defs>

    <rect width="1200" height="630" fill="url(#page)"/>
    <circle cx="1050" cy="90" r="420" fill="url(#glow)"/>
    <path d="M760 630 C820 530 1025 485 1200 500 L1200 630 Z" fill="#bef5f6" opacity="0.62"/>
    <path d="M875 630 C950 560 1080 530 1200 545 L1200 630 Z" fill="#01d4df" opacity="0.10"/>

    <rect x="36" y="30" width="1128" height="570" rx="38" fill="#ffffff" fill-opacity="0.90" stroke="#01d4df" stroke-opacity="0.18" filter="url(#shadow)"/>
    <ellipse cx="915" cy="610" rx="285" ry="42" fill="#079a9c" opacity="0.08"/>
  </svg>
`);

const family = await sharp(familyPath)
  .resize({ height: 630, fit: 'inside', withoutEnlargement: false })
  .png()
  .toBuffer();

const logo = await sharp(logoPath)
  .resize({ width: 445, fit: 'inside', withoutEnlargement: false })
  .png()
  .toBuffer();

await sharp(background)
  .composite([
    { input: logo, left: 94, top: 252 },
    { input: family, left: 638, top: 0 },
  ])
  .jpeg({ quality: 92, chromaSubsampling: '4:4:4', progressive: true })
  .toFile(outputPath);

console.log(outputPath);
