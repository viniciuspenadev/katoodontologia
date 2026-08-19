export const site = {
  name: 'Kato Odontologia',
  shortName: 'Kato',
  tagline: 'Guarulhos · desde 1995',
  since: 1995,

  email: 'contato@katoodontologia.com.br',
  social: {
    instagram: 'https://www.instagram.com/katoodontologia',
    facebook: 'https://www.facebook.com/katoodontologia',
  },

  responsible: { name: 'Dr. Nelson Kato', cro: 'CRO-SP 00000' },
} as const;

export const unidades = [
  {
    id: 'macedo',
    n: '01',
    name: 'Unidade Macedo',
    street: 'Rua Silvio Barbosa, 303',
    district: 'Macedo',
    city: 'Guarulhos',
    state: 'SP',
    phone: '(11) 2408-1446',
    phoneHref: 'tel:+551124081446',
    whatsapp: '(11) 96977-7255',
    whatsappHref: 'https://wa.me/5511969777255',
    mapsHref: 'https://www.google.com/maps/search/?api=1&query=Rua+Silvio+Barbosa+303+Macedo+Guarulhos+SP',
  },
  {
    id: 'cidade-maia',
    n: '02',
    name: 'Unidade Cidade Maia',
    street: 'Av. Dr. Renato de Andrade de Maia, 642',
    district: 'Cidade Maia',
    city: 'Guarulhos',
    state: 'SP',
    phone: '(11) 2600-2705',
    phoneHref: 'tel:+551126002705',
    whatsapp: '(11) 97020-7637',
    whatsappHref: 'https://wa.me/5511970207637',
    mapsHref:
      'https://www.google.com/maps/search/?api=1&query=Av+Dr+Renato+de+Andrade+de+Maia+642+Cidade+Maia+Guarulhos+SP',
  },
] as const;
export const primaryWhats = unidades[0].whatsappHref;

export const stats = [
  { value: 30, prefix: '+', suffix: '', label: 'anos de história', icon: 'clock' },
  { value: 2, prefix: '', suffix: '', label: 'unidades', icon: 'pin' },
  { value: 6, prefix: '', suffix: '', label: 'especialidades', icon: 'grid' },
  { value: 4, prefix: '', suffix: '', label: 'especialistas', icon: 'team' },
] as const;

export const historia = [
  { year: '1995', text: 'Formação do Grupo Kato.' },
  { year: '2000', text: 'Atualização de todos os padrões de atendimento.' },
  { year: '2019', text: 'Ampliação da equipe e programa de treinamentos.' },
  { year: '2020', text: 'Adequações para dispor acessibilidade a todos.' },
  { year: '2021', text: 'Protocolos de higienização reforçados.' },
] as const;

export const especialidades = [
  {
    n: '01',
    name: 'Implantes e Próteses',
    body: 'Reabilitação de dentes perdidos, do implante unitário à prótese total, com planejamento prévio.',
  },
  {
    n: '02',
    name: 'Ortodontia',
    body: 'Correção do alinhamento e da mordida, com acompanhamento em todas as fases do tratamento.',
  },
  {
    n: '03',
    name: 'Endodontia',
    body: 'Tratamento de canal para preservar o dente natural quando a polpa já foi comprometida.',
  },
  {
    n: '04',
    name: 'Odontopediatria',
    body: 'Atendimento infantil no ritmo da criança — a primeira consulta define a relação com o dentista.',
  },
  {
    n: '05',
    name: 'Restauração',
    body: 'Reconstrução de dentes com cárie ou fratura, devolvendo forma e função sem exagero estético.',
  },
  {
    n: '06',
    name: 'Clareamento',
    body: 'Clareamento supervisionado, com avaliação prévia de sensibilidade e da condição da gengiva.',
  },
] as const;

export type Profissional = {
  slug: string;
  name: string;
  role: string;
  focus?: string;
  cro?: string;
};
const CRO_PENDENTE = 'CRO: 0000';

export const equipe: readonly Profissional[] = [
  {
    slug: 'nelson-kato',
    name: 'Dr. Nelson Kato',
    role: 'Cirurgião-dentista',
    focus: 'Odontologia Estética',
    cro: CRO_PENDENTE,
  },
  {
    slug: 'renan-kato',
    name: 'Dr. Renan Kato',
    role: 'Cirurgião-dentista',
    focus: 'Implantodontia',
    cro: CRO_PENDENTE,
  },
  {
    slug: 'julio-cesar',
    name: 'Dr. Júlio César',
    role: 'Cirurgião-dentista',
    focus: 'Endodontia',
    cro: CRO_PENDENTE,
  },
  {
    slug: 'leonardo-kato',
    name: 'Dr. Leonardo Kato',
    role: 'Cirurgião-dentista',
    focus: 'Clínica Geral',
    cro: CRO_PENDENTE,
  },
  {
    slug: 'alex-akamine',
    name: 'Dr. Alex Akamine',
    role: 'Cirurgião-dentista',
    focus: 'Implantodontia',
    cro: CRO_PENDENTE,
  },
  {
    slug: 'flavio-cordeiro',
    name: 'Dr. Flávio Cordeiro',
    role: 'Cirurgião-dentista',
    focus: 'Ortodontia',
    cro: CRO_PENDENTE,
  },
  {
    slug: 'mahyara',
    name: 'Dra. Mahyara',
    role: 'Cirurgiã-dentista',
    focus: 'Clínica Geral',
    cro: CRO_PENDENTE,
  },
  {
    slug: 'pamela-sao-jose',
    name: 'Dra. Pamela São José',
    role: 'Cirurgiã-dentista',
    focus: 'Clínica Geral',
    cro: CRO_PENDENTE,
  },
  {
    slug: 'pamella-martins',
    name: 'Dra. Pamella Martins',
    role: 'Cirurgiã-dentista',
    focus: 'Odontopediatria',
    cro: CRO_PENDENTE,
  },
];

export const depoimentos = [
  {
    quote:
      'Tenho problemas de ansiedade e nunca consegui fazer um tratamento odontológico. Na Kato, fiz até um tratamento de canal, algo que jamais imaginei fazer. Jamais imaginei que conseguiria relaxar em um consultório dentário.',
    author: 'Leandro Correa',
  },
  {
    quote:
      'Equipe excelente! Desde o atendimento até os dentistas, sempre muito educados e solícitos.',
    author: 'Juliana Oliveira',
  },
] as const;
