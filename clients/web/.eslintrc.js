module.exports = {
  extends: ['../../.eslintrc.js', 'next/core-web-vitals'],
  settings: {
    'boundaries/elements': [
      { type: 'runtime', pattern: 'src/runtime/*' },
      { type: 'engine', pattern: 'src/engines/*' },
      { type: 'components', pattern: 'src/components/*' },
      { type: 'app', pattern: 'src/app/*' },
    ],
  },
  rules: {
    'boundaries/element-types': [
      'error',
      {
        default: 'disallow',
        rules: [
          {
            from: 'app',
            allow: ['engine', 'components', 'runtime'],
          },
          {
            from: 'engine',
            allow: ['components', 'runtime'],
          },
          {
            from: 'components',
            allow: ['runtime'],
          },
        ],
      },
    ],
  },
};
