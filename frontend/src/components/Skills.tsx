import { strings } from '../locales/ru';

export default function Skills() {
  return (
    <section id="skills" className="px-6 py-20">
      <div className="mx-auto max-w-6xl">
        <h2 className="mb-4 text-center text-3xl font-bold text-white md:text-4xl">
          {strings.skills.heading}
        </h2>
        <p className="mb-12 text-center text-gray-400">{strings.skills.subtitle}</p>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
          {strings.skills.categories.map((group) => (
            <div
              key={group.category}
              className="rounded-2xl border border-white/5 bg-white/5 p-6 transition-all duration-300 hover:border-cyan-500/30"
            >
              <h3 className="mb-4 text-lg font-semibold text-cyan-400">{group.category}</h3>
              <div className="flex flex-wrap gap-2">
                {group.items.map((skill) => (
                  <span
                    key={skill}
                    className="rounded-full border border-white/5 bg-white/5 px-3 py-1 text-sm text-gray-300"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
