import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { SplitText } from 'gsap/SplitText';
import Lenis from 'lenis';
gsap.registerPlugin(ScrollTrigger, SplitText);
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

function initHeader() {
  const header = document.querySelector<HTMLElement>('[data-header]');
  if (!header) return;

  ScrollTrigger.create({
    start: 'top -80',
    end: 99999,
    onToggle: (self) => {
      if (self.isActive) header.setAttribute('data-stuck', '');
      else header.removeAttribute('data-stuck');
    },
  });
}

function initActiveNav() {
  const links = [...document.querySelectorAll<HTMLAnchorElement>('.hdr__link')];

  links.forEach((link) => {
    const id = link.getAttribute('href');
    if (!id?.startsWith('#')) return;
    const target = document.querySelector(id);
    if (!target) return;

    ScrollTrigger.create({
      trigger: target,
      start: 'top 40%',
      end: 'bottom 40%',
      onToggle: (self) => {
        if (self.isActive) {
          links.forEach((l) => l.removeAttribute('aria-current'));
          link.setAttribute('aria-current', 'true');
        }
      },
    });
  });
}

function initSmoothScroll() {
  const lenis = new Lenis({
    duration: 1.05,

    easing: (t: number) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
    smoothWheel: true,
  });
  lenis.on('scroll', ScrollTrigger.update);
  gsap.ticker.add((time) => lenis.raf(time * 1000));
  gsap.ticker.lagSmoothing(0);

  document.querySelectorAll<HTMLAnchorElement>('a[href^="#"]').forEach((a) => {
    a.addEventListener('click', (e) => {
      const id = a.getAttribute('href');
      if (!id || id === '#') return;
      const target = document.querySelector(id);
      if (!target) return;
      e.preventDefault();
      lenis.scrollTo(target as HTMLElement, { offset: -96 });
    });
  });
}

function initReveals() {
  const groups = new Map<Element, Element[]>();

  document.querySelectorAll<HTMLElement>('[data-reveal]').forEach((el) => {
    const parent = el.parentElement ?? document.body;
    const list = groups.get(parent) ?? [];
    list.push(el);
    groups.set(parent, list);
  });

  groups.forEach((els) => {
    gsap.to(els, {
      opacity: 1,
      y: 0,
      duration: 0.9,
      ease: 'power3.out',
      stagger: 0.08,
      scrollTrigger: {
        trigger: els[0],
        start: 'top 88%',
        once: true,
      },
    });
  });
}

function initHeadline() {
  const h1 = document.querySelector<HTMLElement>('[data-reveal-lines]');
  if (!h1) return;
  if (window.matchMedia('(width < 62rem)').matches) return;

  document.fonts.ready.then(() => {
    const split = new SplitText(h1, { type: 'lines', linesClass: 'line' });
    gsap.set(h1, { opacity: 1, y: 0 });
    gsap.set(split.lines, { overflow: 'hidden' });

    gsap.from(split.lines, {
      yPercent: 110,
      duration: 1.1,
      ease: 'power4.out',
      stagger: 0.09,
      delay: 0.15,
    });
  });
}

function initCounters() {
  document.querySelectorAll<HTMLElement>('[data-count]').forEach((el) => {
    const target = Number(el.dataset.count ?? 0);
    if (!Number.isFinite(target)) return;
    const decimals = Number(el.dataset.countDecimals ?? 0);
    const state = { v: 0 };

    gsap.to(state, {
      v: target,
      duration: 1.6,
      ease: 'power2.out',
      scrollTrigger: { trigger: el, start: 'top 85%', once: true },
      onUpdate: () => {
        el.textContent = state.v.toLocaleString('pt-BR', {
          minimumFractionDigits: decimals,
          maximumFractionDigits: decimals,
        });
      },
      onComplete: () => {
        el.textContent = target.toLocaleString('pt-BR', {
          minimumFractionDigits: decimals,
          maximumFractionDigits: decimals,
        });
      },
    });
  });
}

function initHistoryDrum() {
  const section = document.querySelector<HTMLElement>('[data-drum-section]');
  const drum = document.querySelector<HTMLElement>('[data-drum]');
  const wheel = document.querySelector<HTMLElement>('[data-drum-wheel]');
  if (!section || !drum || !wheel) return;
  if (!window.matchMedia('(width >= 62rem)').matches) return;
  const faces = [...drum.querySelectorAll<HTMLElement>('[data-face]')];
  const ticks = [...document.querySelectorAll<HTMLElement>('[data-rail-item]')];
  const n = faces.length;
  if (n < 2) return;
  const stepDeg = 360 / n;
  drum.classList.add('is-live');
  const state = { i: 0 };

  const render = () => {
    wheel.style.setProperty('--rot', `${-state.i * stepDeg}deg`);

    faces.forEach((face, idx) => {
      const d = Math.abs(idx - state.i);
      face.style.opacity = String(gsap.utils.clamp(0, 1, 1 - d * 1.05));
      face.style.filter = d > 0.04 ? `blur(${Math.min(d * 4, 7)}px)` : 'none';
    });
    const active = Math.round(state.i);
    ticks.forEach((t, idx) => {
      if (idx === active) t.setAttribute('data-active', '');
      else t.removeAttribute('data-active');
    });
  };
  render();

  gsap.to(state, {
    i: n - 1,
    ease: 'none',
    onUpdate: render,
    scrollTrigger: {
      trigger: section,
      start: 'top top',

      end: () => `+=${(n - 1) * window.innerHeight * 0.8}`,
      pin: true,
      pinSpacing: true,
      scrub: 0.6,
      invalidateOnRefresh: true,
    },
  });
}

function initTeamMarquee() {
  const car = document.querySelector<HTMLElement>('[data-carousel]');
  const viewport = car?.querySelector<HTMLElement>('[data-viewport]');
  const track = car?.querySelector<HTMLElement>('[data-track]');
  if (!car || !viewport || !track) return;
  const originals = [...track.children] as HTMLElement[];
  if (!originals.length) return;
  const PPS = 42;
  const TAP = 8;
  const touch = window.matchMedia('(hover: none)');
  let tween: gsap.core.Tween | null = null;
  let trigger: ScrollTrigger | null = null;
  let glide: gsap.core.Tween | null = null;

  const speed = (v: number) =>
    tween && gsap.to(tween, { timeScale: v, duration: 0.5, overwrite: true });

  const seek = (t: number) => {
    if (!tween) return;
    const d = tween.duration();
    tween.time(((t % d) + d) % d);
  };

  const closeAll = () => {
    track.querySelectorAll<HTMLElement>('.is-open').forEach((el) => el.classList.remove('is-open'));
  };

  const toggle = (card: HTMLElement | null) => {
    const wasOpen = card?.classList.contains('is-open');
    closeAll();
    if (card && !wasOpen) card.classList.add('is-open');
    speed(card && !wasOpen ? 0.25 : 1);
  };

  const build = () => {
    tween?.kill();
    trigger?.kill();
    glide?.kill();
    gsap.set(track, { x: 0 });
    track.replaceChildren(...originals);
    const gap = parseFloat(getComputedStyle(track).gap) || 0;
    const setWidth = track.scrollWidth + gap;
    if (setWidth <= 0) return;
    const copies = Math.min(12, Math.max(2, Math.ceil((viewport.clientWidth * 2) / setWidth) + 1));

    for (let c = 1; c < copies; c++) {
      originals.forEach((node) => {
        const clone = node.cloneNode(true) as HTMLElement;
        clone.setAttribute('aria-hidden', 'true');
        clone.querySelectorAll('a, button').forEach((el) => el.setAttribute('tabindex', '-1'));
        track.appendChild(clone);
      });
    }
    car.setAttribute('data-live', '');

    tween = gsap.to(track, {
      x: -setWidth,
      duration: setWidth / PPS,
      ease: 'none',
      repeat: -1,
    });

    trigger = ScrollTrigger.create({
      trigger: car,
      start: 'top bottom',
      end: 'bottom top',
      onToggle: (self) => (self.isActive ? tween?.play() : tween?.pause()),
    });
  };
  build();
  let dragging = false;
  let downCard: HTMLElement | null = null;
  let originX = 0;
  let originT = 0;
  let travel = 0;
  let lastX = 0;
  let lastAt = 0;
  let velocity = 0;

  viewport.addEventListener('pointerdown', (e) => {
    if (!tween || (e.pointerType === 'mouse' && e.button !== 0)) return;
    glide?.kill();
    dragging = true;
    downCard = (e.target as Element | null)?.closest<HTMLElement>('[data-card]') ?? null;
    travel = 0;
    originX = lastX = e.clientX;
    originT = tween.time();
    lastAt = e.timeStamp;
    velocity = 0;
    tween.pause();
    car.classList.add('is-dragging');
    viewport.setPointerCapture(e.pointerId);
  });

  viewport.addEventListener('pointermove', (e) => {
    if (!dragging) return;
    const dx = e.clientX - originX;
    travel = Math.max(travel, Math.abs(dx));
    const dt = e.timeStamp - lastAt;
    if (dt > 0) velocity = ((e.clientX - lastX) / dt) * 1000;
    lastX = e.clientX;
    lastAt = e.timeStamp;
    seek(originT - dx / PPS);
  });

  const release = (e: PointerEvent) => {
    if (!dragging) return;
    dragging = false;
    car.classList.remove('is-dragging');
    if (viewport.hasPointerCapture(e.pointerId)) viewport.releasePointerCapture(e.pointerId);

    if (travel <= TAP) {
      if (touch.matches) toggle(downCard);
      tween?.play();
      return;
    }
    const from = { t: tween?.time() ?? 0 };
    glide = gsap.to(from, {
      t: from.t - gsap.utils.clamp(-1.4, 1.4, (velocity / PPS) * 0.4),
      duration: 0.9,
      ease: 'power3.out',
      onUpdate: () => seek(from.t),
      onComplete: () => {
        if (!dragging) tween?.play();
      },
    });
  };
  viewport.addEventListener('pointerup', release);
  viewport.addEventListener('pointercancel', release);

  car.addEventListener('pointerenter', () => {
    if (!touch.matches && !dragging) speed(0.25);
  });
  car.addEventListener('pointerleave', () => {
    if (!touch.matches && !dragging) speed(1);
  });
  car.addEventListener('focusin', () => speed(0.25));
  car.addEventListener('focusout', () => speed(1));

  document.addEventListener('pointerdown', (e) => {
    if (!touch.matches) return;
    if ((e.target as Element | null)?.closest('[data-carousel]')) return;
    closeAll();
    speed(1);
  });
  let resizeId = 0;
  window.addEventListener('resize', () => {
    window.clearTimeout(resizeId);
    resizeId = window.setTimeout(build, 250);
  });
}

function initParallax() {
  if (window.matchMedia('(width < 62rem)').matches) return;

  document.querySelectorAll<HTMLElement>('[data-parallax]').forEach((el) => {
    const strength = Number(el.dataset.parallax ?? 0.05);
    gsap.to(el, {
      yPercent: strength * 100,
      ease: 'none',
      scrollTrigger: {
        trigger: el,
        start: 'top bottom',
        end: 'bottom top',
        scrub: true,
      },
    });
  });
}

function start() {
  initHeader();
  initActiveNav();

  if (reducedMotion.matches) {
    return;
  }
  initSmoothScroll();
  initHeadline();
  initReveals();
  initCounters();
  initHistoryDrum();
  initTeamMarquee();
  initParallax();
  document.fonts.ready.then(() => ScrollTrigger.refresh());
  window.addEventListener('load', () => ScrollTrigger.refresh());
}
start();
reducedMotion.addEventListener('change', () => window.location.reload());
