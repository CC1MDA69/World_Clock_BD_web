/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
    "./*.html",        // Все HTML файлы в корне
    "./src/**/*.{html,js}" // Если файлы в папке src
        ], // укажите путь к вашим html файлам
  theme: {
    extend: {},
  },
  plugins: [],
}
