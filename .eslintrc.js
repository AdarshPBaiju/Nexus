module.exports = {
  root: true,
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint', 'boundaries'],
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
  ],
  rules: {
    'max-lines': ['error', { max: 350, skipBlankLines: true, skipComments: true }],
    'max-lines-per-function': ['error', { max: 35, skipBlankLines: true, skipComments: true }],
    'max-params': ['error', 4],
    'complexity': ['error', 10],
    'max-depth': ['error', 3],
    '@typescript-eslint/no-explicit-any': 'error',
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
  },
  overrides: [
    {
      files: ['**/*.tsx'],
      rules: {
        'max-lines': ['error', { max: 250, skipBlankLines: true, skipComments: true }],
      },
    },
    {
      files: ['packages/contracts/**'],
      rules: {
        'max-lines': ['error', { max: 500, skipBlankLines: true, skipComments: true }],
      },
    },
  ],
};
