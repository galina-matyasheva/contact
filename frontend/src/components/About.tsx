import { strings } from '../locales/ru';

export default function About() {
  return (
    <section id="about" className="px-6 py-20">
      <div className="mx-auto max-w-4xl">
        <h2 className="mb-12 text-center text-3xl font-bold text-white md:text-4xl">
          {strings.about.heading}
        </h2>

        <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
          <div className="space-y-4 leading-relaxed text-gray-300 md:col-span-2">
            {strings.about.bio.map((paragraph, i) => (
              <p key={i}>{paragraph}</p>
            ))}
          </div>

          <div className="space-y-4">
            {strings.about.stats.map((stat) => (
              <div
                key={stat.label}
                className="rounded-xl border border-white/5 bg-white/5 p-4 text-center"
              >
                <div className="text-3xl font-bold text-cyan-400">{stat.value}</div>
                <div className="mt-1 text-sm text-gray-400">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
