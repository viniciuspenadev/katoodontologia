# Kato Odontologia — site

Astro 7 + TypeScript estrito. Site estático, sem framework de UI.
Tema escuro único, derivado da identidade do logo (teal/prata).

```bash
npm run dev
```

## Estrutura

```
src/styles/tokens.css    todas as decisões de design como variáveis — comece aqui
src/styles/base.css      reset, títulos, .em, botões, .eyebrow, estado de reveal
src/data/site.ts         telefone, endereço, horários, CRO — nada é hardcoded nos componentes
src/scripts/motion.ts    Lenis + GSAP (ScrollTrigger, SplitText) e a saída por reduced-motion
src/components/          uma seção por arquivo, CSS com escopo dentro
src/layouts/Base.astro   head, fontes, meta, skip-link
```

## Deploy — GitHub + EasyPanel

Build em dois estágios no `Dockerfile`: Node 22 compila o site, nginx serve o
`dist/`. Não sobe Node em produção — a imagem final é só nginx + arquivos
estáticos.

### 1. Subir para o GitHub

```bash
git init -b main
git add .
git commit -m "Site Kato Odontologia"
git remote add origin git@github.com:SEU-USUARIO/kato.git
git push -u origin main
```

Repositório privado: o `deliverables/` guarda o briefing do cliente.

### 2. Criar o serviço no EasyPanel

1. **Project → + Service → App**, nome `kato`.
2. **Source:** GitHub → repositório e branch `main`.
3. **Build:** método **Dockerfile**, arquivo `Dockerfile` na raiz.
4. **Deploy.** A primeira build leva alguns minutos: o Astro gera ~90 variantes
   de imagem.
5. **Domains:** `katoodontologia.com.br` e `www.katoodontologia.com.br`,
   porta **80**, HTTPS ligado. O Let's Encrypt só emite o certificado depois que
   o registro A do DNS apontar para o IP da VPS.
6. **Auto deploy** ligado: cada `push` na `main` republica sozinho.

### Domínio

O site está em produção em `https://katoodontologia.com.br`, que é o padrão de
`astro.config.mjs`. Desse endereço saem a URL canônica e o `og:image` — que
precisam ser absolutos, e apontar para o host onde o arquivo realmente está: se
apontarem para outro domínio, o WhatsApp busca a imagem lá, recebe 404 e mostra
o link sem foto.

Para publicar uma prévia em outro host, passe no EasyPanel **Build → Build
args**: `SITE_URL=https://outro-host`. Fora de `katoodontologia.com.br` a página
sai com `<meta name="robots" content="noindex">`, para a prévia não competir com
o site oficial no Google. O `Dockerfile` já declara `ARG SITE_URL`; se a
variável chegar vazia ou malformada, o build não quebra: cai no padrão.

### HTTPS

O certificado (Let's Encrypt) e o redirect de HTTP para HTTPS ficam no Traefik
do EasyPanel — basta o HTTPS ligado em cada domínio. O `nginx.conf` completa:

- `www.katoodontologia.com.br` redireciona (301) para `katoodontologia.com.br`;
- `Strict-Transport-Security` com um ano, sem `includeSubDomains`. O navegador
  guarda a regra: se o certificado falhar, o visitante não consegue ignorar o
  aviso. Para desfazer, publique `max-age=0` antes de tirar o cabeçalho;
- `absolute_redirect off`, para que os redirects do nginx não saiam como
  `http://` — ele só enxerga HTTP, porque o TLS termina no Traefik.

### package-lock.json

A imagem de build é `node:24`, que traz o mesmo npm 11 usado no desenvolvimento.
Isso não é detalhe: o npm 10 e o npm 11 divergem sobre quais dependências
opcionais de plataforma ficam registradas no lock, e um lock escrito por um
falha no `npm ci` do outro. Se trocar a versão do Node aqui, confira que o npm
da imagem é o mesmo que gerou o lock — ou rode `npm ci --dry-run` com os dois
antes de subir.

### Memória da VPS

O `astro build` processa as imagens com sharp e a maior fonte tem 4480×6720
(14 MB). Em VPS de 1 GB isso pode estourar a memória. Saídas: ligar swap no
Ubuntu, ou reduzir `src/assets/equipe/renan-kato.jpg` para 2560px de largura —
que é o maior recorte que o site pede.

### Prévia no WhatsApp

`public/brand/og-kato.jpg` (1200×630, 65 kB) é o cartão que aparece quando o
link é compartilhado. As tags `og:` e `twitter:` saem de `src/layouts/Base.astro`
com URL absoluta.

O WhatsApp guarda a prévia em cache por semanas, por URL. Se um link já foi
enviado antes da correção, ele continua mostrando o resultado antigo: para testar
de novo, mande o endereço com um parâmetro qualquer (`?v=2`), que para o
rastreador é outra URL. Trocar a arte pede a mesma coisa — troque o nome do
arquivo (`og-kato-2.jpg`), senão o link continua servindo a imagem velha.

Para conferir antes de divulgar, use o
[Sharing Debugger do Facebook](https://developers.facebook.com/tools/debug/),
que é o mesmo rastreador do WhatsApp, e o botão *Scrape Again*.

## Pendências antes de publicar

- [ ] **Logo vetorial** → `public/brand/kato-logo.svg`, depois seguir as instruções
      no topo de `src/components/Logo.astro` (hoje o lockup é reproduzido em tipo).
- [ ] **Fotos reais** → substituir `public/brand/hero-placeholder.svg` (proporções
      3:4 e 4:5, mínimo 1440px de largura). Converter para AVIF/WebP e trocar
      `<img>` por `<Picture>` de `astro:assets`.
- [ ] **Dados reais** em `src/data/site.ts` — todo campo marcado `TODO`.
- [ ] **CRO de cada profissional.** Os nove estão com `CRO_PENDENTE`
      (`'CRO: 0000'`, no topo da lista `equipe` em `src/data/site.ts`) só para o
      cartão ficar completo. **Isto não pode ir ao ar**: a Resolução CFO-196/2019
      exige o número verdadeiro em peça publicitária. Troque cada
      `cro: CRO_PENDENTE` pelo valor da pessoa.
- [ ] **Sobrenome da Dra. Mahyara** — é a única sem sobrenome na lista.
- [ ] **Números da seção de estatísticas** (`stats`) precisam ser verificáveis.
      A Resolução CFO-196/2019 proíbe alegação sem comprovação. Pendente hoje:
      o contador diz "4 especialistas" e a fita publica nove pessoas.
- [ ] **Responsável técnico + CRO** no rodapé (obrigatório).
- [ ] Revisar a copy com a clínica — o texto atual é uma proposta de voz, não
      conteúdo aprovado.

Para acrescentar alguém à equipe: foto em `src/assets/equipe/<slug>.jpg`
(retrato, mín. 720×960, rosto no terço superior — o recorte é 3:4 com
`object-position: 50% 20%`) e uma linha em `equipe` com o mesmo `slug`. O
carrossel se ajusta sozinho à quantidade. `focus` (especialidade) e `cro` são
opcionais e só aparecem se preenchidos — são o que o cartão revela ao abrir.

## Skills instaladas

`.claude/skills/` contém:

| Skill | Origem | Papel |
| --- | --- | --- |
| `kato-design-system` | própria | **autoridade estética** — cores, tipo, layout, motion, voz, lista de proibições |
| `gsap-scrolltrigger` | freshtechbro | referência de API do GSAP |
| `motion-framer` | freshtechbro | referência de motion (não usado hoje — sem React no projeto) |
| `locomotive-scroll` | freshtechbro | referência de smooth scroll |
| `lottie-animations` | freshtechbro | referência para animações vetoriais, se entrarem |
| `modern-web-design` | freshtechbro | **rebaixada** a referência técnica de performance/a11y; a descrição foi reescrita para não competir com o design system |

As 17 skills restantes do repositório (Three.js, Babylon, A-Frame, PlayCanvas,
PixiJS, Blender, Substance 3D etc.) foram deliberadamente deixadas de fora.

## Performance

Build atual: HTML 23 KB, CSS 25 KB, JS 137 KB não comprimido (~45 KB gzip —
GSAP core + ScrollTrigger + SplitText + Lenis). O JS é módulo diferido e não
bloqueia render. Se o peso incomodar, o caminho é importar `SplitText` e o
parallax dinamicamente só em telas ≥ 62rem.
