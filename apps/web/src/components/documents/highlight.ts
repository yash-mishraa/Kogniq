export const highlightPattern = (text: string, pattern: string) => {
  return text.replace(new RegExp(pattern, 'gi'), match => `<mark class="bg-yellow-200">${match}</mark>`);
};
