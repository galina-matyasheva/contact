import { strings } from '../locales/ru';

export default function Header() {
  return (
    <header className="fixed top-0 right-0 left-0 z-50 border-b border-white/5 bg-black/60 backdrop-blur-md">
      <a
        href="#about"
        className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-[100] focus:rounded-lg focus:bg-cyan-500 focus:px-4 focus:py-2 focus:text-white"
      >
        {strings.nav.skipToContent}
      </a>
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <a href="#" className="text-xl font-bold text-white">
          dev<span className="text-cyan-400">.portfolio</span>
        </a>
        <div className="hidden items-center gap-8 md:flex">
          <a href="#about" className="text-gray-300 transition-colors hover:text-white">
            {strings.nav.about}
          </a>
          <a href="#skills" className="text-gray-300 transition-colors hover:text-white">
            {strings.nav.skills}
          </a>
          <a href="#contact" className="text-gray-300 transition-colors hover:text-white">
            {strings.nav.contact}
          </a>
        </div>
        <a
          href="#contact"
          className="rounded-lg border border-cyan-500/30 bg-cyan-500/10 px-4 py-2 text-sm font-medium text-cyan-400 transition-all hover:bg-cyan-500/20"
        >
          {strings.nav.write}
        </a>
      </nav>
    </header>
  );
}
