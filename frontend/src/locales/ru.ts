export const strings = {
  nav: {
    skipToContent: 'Перейти к контенту',
    about: 'Обо мне',
    skills: 'Навыки',
    contact: 'Контакт',
    write: 'Написать',
  },
  hero: {
    available: 'Открыт к предложениям',
    greeting: 'Привет, я',
    role: 'Разработчик',
    description:
      'Создаю современные веб-приложения с фокусом на качество кода, производительность и отличный пользовательский опыт.',
    contactCta: 'Связаться со мной',
    learnMore: 'Узнать больше',
  },
  about: {
    heading: 'Обо мне',
    bio: [
      'Fullstack-разработчик с опытом создания веб-приложений различного масштаба — от лендингов до сложных SaaS-платформ.',
      'Специализируюсь на React/TypeScript на фронтенде и node.js/Rython на бэкенде. Умею применять AI-инструменты для повышения продуктивности и создания умных функций.',
      'Стремлюсь к чистому, тестируемому коду и продуманной архитектуре. Верю, что хорошая кодовая база — это инвестиция в будущее проекта.',
    ],
    stats: [
      { label: 'Проектов', value: '20+' },
      { label: 'Лет опыта', value: '5+' },
      { label: 'Стек технологий', value: '15+' },
    ],
  },
  skills: {
    heading: 'Мои навыки',
    subtitle: 'Технологии и инструменты, с которыми я работаю',
    categories: [
      {
        category: 'Frontend',
        items: ['JavaScript', 'React', 'TypeScript', 'Next.js'],
      },
      {
        category: 'Backend',
        items: ['Python', 'Node.js', 'MySQL', 'MongoDB'],
      },
      {
        category: 'DevOps & Tools',
        items: ['Docker', 'Git', 'CI/CD', 'Linux'],
      },
      {
        category: 'AI & Data',
        items: ['OpenCode', 'Claude Code', 'Antigravity', 'Prompt Engineering'],
      },
    ],
  },
  contact: {
    heading: 'Связаться со мной',
    subtitle: 'Есть проект или идея? Напишите мне, и я отвечу в ближайшее время.',
    success: 'Сообщение успешно отправлено! Спасибо за обращение.',
    fields: {
      name: { label: 'Ваше имя', placeholder: 'Ваше имя' },
      phone: { label: 'Телефон', placeholder: 'Телефон' },
      email: { label: 'Email', placeholder: 'Email' },
      comment: { label: 'Сообщение', placeholder: 'Ваше сообщение...' },
    },
    validation: {
      name: 'Имя должно содержать минимум 2 символа',
      phone: 'Введите корректный номер телефона',
      email: 'Введите корректный email',
      comment: 'Комментарий должен содержать минимум 5 символов',
    },
    submit: {
      idle: 'Отправить сообщение',
      loading: 'Отправка...',
      error: 'Ошибка отправки. Попробуйте позже.',
    },
  },
  footer: {
    copyright: 'Developer Portfolio. Все права защищены.',
    github: 'GitHub',
    linkedin: 'LinkedIn',
    telegram: 'Telegram',
  },
  errorBoundary: {
    heading: 'Что-то пошло не так',
    message: 'Попробуйте обновить страницу',
  },
  api: {
    fallbackError: 'Произошла ошибка',
  },
} as const;
