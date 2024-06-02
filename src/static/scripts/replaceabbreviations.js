function replaceAbbreviations(inputString) {
    // Regular expression to find the pattern: short form (full form)
    const pattern = /(\b[A-Z]{2,}\b)\s?\(([^)]+)\)/g;

    // Replace all matches in the input string
    const result = inputString.replace(pattern, (match, shortForm, fullForm) => {
        return `<abbr title='${fullForm}'>${shortForm}</abbr>`;
    });

    return result;
}