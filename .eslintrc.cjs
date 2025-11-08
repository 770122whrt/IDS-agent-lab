const { resolve } = require('node:path')

const project = resolve(process.cwd(), 'tsconfig.json')

/** @type {import('eslint').Linter.Config} */
module.exports = {
  extends: [
    "prettier",
    require.resolve('@vercel/style-guide/eslint/node'),
    require.resolve('@vercel/style-guide/eslint/browser'),
    require.resolve('@vercel/style-guide/eslint/typescript'),
    require.resolve('@vercel/style-guide/eslint/react'),
    require.resolve('@vercel/style-guide/eslint/next'),
  ],
  parserOptions: {
    project: project,
    tsconfigRootDir: __dirname,
  },
  globals: {
    React: true,
    JSX: true
  },
  settings: {
    'import/resolver': {
      typescript: {
        project
      }
    }
  },
  ignorePatterns: ['node_modules/', 'dist/', '**/components/ui/**', '**/components/motion/**', 'tailwind.config.ts'],
  rules: {
    'no-console': 'off',
    'no-unused-vars': 'off',
    'import/no-default-export': 'off',
    'import/order': 'off',
    'react/no-array-index-key': 'off',
    'react/jsx-sort-props': 'off',
    'react/jsx-no-leaked-render': 'off',
    'tsdoc/syntax': 'off',
    'eslint-comments/require-description': 'off',
    '@typescript-eslint/consistent-type-definitions': 'off',
    '@typescript-eslint/explicit-function-return-type': 'off',
    '@typescript-eslint/no-unused-vars': 'off',
    '@typescript-eslint/no-shadow': 'off',
    '@typescript-eslint/restrict-template-expressions': 'off',
    // best practices with warnings
    'no-else-return': 'warn',
    'no-useless-return': 'warn',
    'object-shorthand': 'warn',
    'prefer-template': 'warn',
    'react/jsx-boolean-value': 'warn',
    '@typescript-eslint/consistent-type-imports': 'warn',
    '@typescript-eslint/prefer-nullish-coalescing': 'warn',
    '@typescript-eslint/prefer-optional-chain': 'warn',
    // payload specific off rules, local api currently heavily relies on any
    '@typescript-eslint/no-explicit-any': 'off',
    '@typescript-eslint/no-unsafe-assignment': 'off',
    '@typescript-eslint/no-unsafe-return': 'off',
    '@typescript-eslint/no-unsafe-member-access': 'off',
    '@typescript-eslint/no-unsafe-argument': 'off',
    '@typescript-eslint/no-unsafe-call': 'off',
    // temporary rules
    // '@typescript-eslint/no-unnecessary-condition': 'warn',
  }
};
