import { defineConfig } from 'astro/config';

const preferido = process.env.SITE_URL?.trim();
const site = preferido && URL.canParse(preferido) ? preferido : 'https://katoodontologia.com.br';

export default defineConfig({
  site,
});
