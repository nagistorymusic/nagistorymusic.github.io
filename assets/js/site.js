// 3案で共通の仕組み：作品データ／クリックで再生／文字アニメーション／ベイート
window.NSM = (() => {
  const works = [
    { title: 'Halloween Night', id: '13-gX6KvSuo', line: '何が起きても不思議じゃない——\nそんな、一夜限りの物語。' },
    { title: 'Black Vinyl', id: 'Plytn7F-Xco', line: '歌詞をなぞると、扉が開く。' },
    { title: 'Twist the World', id: 'Hlx6cZSQH5w', line: '世界を書き換える魔術師。\nその力を得た時、\nあなたはどうしますか？' },
    { title: '札あつめ', id: 'g14MSpKOfrk', line: '海の彼方、妖どもが集う島' },
    { title: '道化師と僕', id: 'YRiRkiDy_ZY', line: 'ルールは守らない。\n美しければそれでいい。' },
    { title: '物語の在る処', id: 'FIB8b6Nw2I8', line: '二人は今日も旅をつづける。' },
  ];
  const links = [
    ['YouTube', 'https://www.youtube.com/@Nagi-Story-Music'],
    ['TikTok', 'https://www.tiktok.com/@nagistorymusic'],
    ['X', 'https://x.com/Nagi_storymusic'],
    ['note', 'https://note.com/nagi_storymusic'],
  ];
  const profile = {
    ja: '物語・音楽・映像を組み合わせて作品を制作するクリエイター。2025年10月、Sunoとの出会いをきっかけに音楽制作を始め、オリジナルの短編小説と、そこから生まれた楽曲をYouTubeで公開。AIを創作の相棒として、物語の世界を楽曲やミュージックビデオへ広げている。',
    en: 'Nagi is a creator who brings together storytelling, music, and visuals. After discovering Suno in October 2025, Nagi began making music and sharing original short stories and the songs they inspired on YouTube. With AI as a creative partner, Nagi brings these story worlds to life through songs and music videos.',
  };
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const thumb = (id) => `https://i.ytimg.com/vi/${id}/maxresdefault.jpg`;
  // サイト内に置いた軽いサムネイル（assets/works/<id>-640.webp / -1280.webp）
  const localThumb = (id, base = '') => ({
    src: `${base}assets/works/${id}-1280.webp`,
    srcset: `${base}assets/works/${id}-640.webp 640w, ${base}assets/works/${id}-1280.webp 1280w`,
  });

  // クリックした時だけ YouTube を読み込む（ふだんはサムネイルだけ）
  function facade(el, id) {
    el.addEventListener('click', () => {
      const f = document.createElement('iframe');
      f.src = `https://www.youtube-nocookie.com/embed/${id}?autoplay=1&rel=0`;
      f.allow = 'autoplay; encrypted-media; picture-in-picture';
      f.allowFullscreen = true;
      el.replaceChildren(f);
      el.classList.add('is-playing');
    }, { once: true });
  }

  // 04 テキストリビール：1文字ずつ span に分ける
  function split(el) {
    const text = el.textContent;
    el.textContent = '';
    el.setAttribute('aria-label', text.replace(/\n/g, ' '));
    [...text].forEach((ch, i) => {
      if (ch === '\n') { el.append(document.createElement('br')); return; }
      const s = document.createElement('span');
      s.className = 'ch';
      s.setAttribute('aria-hidden', 'true');
      s.style.setProperty('--i', i);
      s.textContent = ch === ' ' ? ' ' : ch;
      el.append(s);
    });
  }

  // 画面に入ったら .is-in を付ける（01/04/05/06 の発火用）
  function reveal(selector = '[data-reveal]') {
    const els = document.querySelectorAll(selector);
    if (reduced) { els.forEach((e) => e.classList.add('is-in')); return; }
    // clip-path で完全に隠した要素は交差判定されないので、親要素で見る
    const owner = new Map();
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (!e.isIntersecting) return;
        (owner.get(e.target) || []).forEach((el) => el.classList.add('is-in'));
        io.unobserve(e.target);
      });
    }, { threshold: 0.2 });
    els.forEach((el) => {
      const t = el.hasAttribute('data-mask') ? el.parentElement : el;
      owner.set(t, [...(owner.get(t) || []), el]);
      io.observe(t);
    });
  }

  // ベイート：mode 'follow' = あとからついてくる / 'gaze' = 隅にいて目線だけ追う
  function mascot({ src, side, mode = 'follow', size = 72, corner = 'right', tapToTop = false } = {}) {
    const fine = matchMedia('(pointer: fine)').matches;
    if (!fine) size = Math.round(size * 0.6); // スマホでは小さく隅に
    const wrap = document.createElement('div');
    wrap.className = 'bairt';
    wrap.innerHTML = `<img src="${src}" alt="" width="${size}">`;
    document.body.append(wrap);
    // スマホではタップで一番上へ戻るボタンになる
    if (tapToTop && !fine) {
      wrap.setAttribute('role', 'button');
      wrap.setAttribute('aria-label', 'ページの一番上へ');
      wrap.tabIndex = 0;
      wrap.style.pointerEvents = 'auto';
      wrap.style.cursor = 'pointer';
      const go = () => {
        wrap.querySelector('img').animate(
          [{ transform: 'translateY(0)' }, { transform: 'translateY(-14px)' }, { transform: 'translateY(0)' }],
          { duration: 420, easing: 'cubic-bezier(.3,.7,.3,1)' });
        scrollTo({ top: 0, behavior: reduced ? 'auto' : 'smooth' });
      };
      wrap.addEventListener('click', go);
      wrap.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); go(); } });
    }
    const img = wrap.querySelector('img');
    let facing = 'front';
    let x = innerWidth - size - 32, y = innerHeight - size * 2.4 - 24;
    let tx = x, ty = y, mx = x, my = y, t = 0;
    if (corner === 'left') { x = tx = 24; }
    addEventListener('pointermove', (e) => {
      mx = e.clientX; my = e.clientY;
      if (mode === 'follow') {
        // カーソルの右下に少し離れてつく（文字や作品を隠さないため）
        tx = Math.min(innerWidth - size - 16, mx + 36);
        ty = Math.min(innerHeight - size * 2.4 - 16, my + 28);
      }
    });
    // 作品の上ではふちへ退避
    document.addEventListener('pointerover', (e) => {
      if (mode === 'follow' && e.target.closest('[data-avoid]')) { tx = innerWidth - size - 24; }
    });
    const tick = () => {
      t += 1 / 60;
      const bob = reduced ? 0 : Math.sin(t * 2) * 6;
      if (mode === 'follow' && fine && !reduced) {
        const dx = tx - x;
        x += dx * 0.06; y += (ty - y) * 0.06;
        wrap.style.transform = `translate(${x}px, ${y + bob}px) rotate(${Math.max(-12, Math.min(12, dx * 0.08))}deg)`;
      } else {
        // 目線だけ：カーソルが離れたら横を向き、体を少しそちらへ傾ける
        const dx = mx - (x + size / 2);
        const want = !fine || reduced || Math.abs(dx) < 220 || !side ? 'front' : (dx < 0 ? 'left' : 'right');
        if (want !== facing) {
          facing = want;
          img.src = want === 'front' ? src : side;
          img.style.transform = want === 'right' ? 'scaleX(-1)' : '';
        }
        const tilt = fine && !reduced ? Math.max(-6, Math.min(6, dx * 0.01)) : 0;
        wrap.style.transform = `translate(${x}px, ${y + bob}px) rotate(${tilt}deg)`;
      }
      requestAnimationFrame(tick);
    };
    tick();
  }

  // 16 マーキー：スクロールの速さで加速
  function marquee(el) {
    const track = el.querySelector('.track');
    let pos = 0, last = scrollY, boost = 0;
    const loop = () => {
      const v = scrollY - last; last = scrollY;
      boost = boost * 0.9 + Math.abs(v) * 0.15;
      if (!reduced) pos -= 0.6 + boost;
      const w = track.scrollWidth / 2;
      if (-pos > w) pos += w;
      track.style.transform = `translateX(${pos}px)`;
      requestAnimationFrame(loop);
    };
    loop();
  }

  // 14 テキストフィル：要素の位置に合わせて --p を 0→1
  function fill(el) {
    const on = () => {
      const r = el.getBoundingClientRect();
      const p = Math.min(1, Math.max(0, (innerHeight * 0.85 - r.top) / (r.height + innerHeight * 0.45)));
      el.style.setProperty('--p', reduced ? 1 : p);
    };
    addEventListener('scroll', on, { passive: true }); on();
  }

  return { works, links, profile, reduced, thumb, localThumb, facade, split, reveal, mascot, marquee, fill };
})();
