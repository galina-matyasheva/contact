import { strings } from '../locales/ru';

export default function Hero() {
  return (
    <section className="flex min-h-screen items-center justify-center px-6 pt-20">
      <div className="mx-auto max-w-4xl text-center">
        <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-cyan-500/20 bg-cyan-500/10 px-4 py-2 text-sm text-cyan-400">
          <span className="h-2 w-2 animate-pulse rounded-full bg-green-400" />
          {strings.hero.available}
        </div>

        <h1 className="mb-6 text-5xl leading-tight font-bold text-white md:text-7xl">
          {strings.hero.greeting}{' '}
          <span className="bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
            {strings.hero.role}
          </span>
        </h1>

        <p className="mx-auto mb-10 max-w-2xl text-xl leading-relaxed text-gray-400 md:text-2xl">
          {strings.hero.description}
        </p>

        <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
          <a
            href="#contact"
            className="rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 px-8 py-4 text-lg font-semibold text-white transition-all hover:scale-105 hover:shadow-lg hover:shadow-cyan-500/25"
          >
            {strings.hero.contactCta}
          </a>
          <a
            href="#about"
            className="rounded-xl border border-white/10 px-8 py-4 text-lg font-medium text-gray-300 transition-all hover:border-white/20 hover:text-white"
          >
            {strings.hero.learnMore}
          </a>
        </div>
      </div>
    </section>
  );
}
