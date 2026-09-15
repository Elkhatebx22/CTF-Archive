const { JSDOM } = require('jsdom');

function sanitize(html) {
    if (html.length > 1000) {
        return "Content is too long.";
    }
    try {
        const { window: { document, NodeFilter } } = new JSDOM(html);
        const nodeIterator = document.createNodeIterator(document.body, NodeFilter.SHOW_COMMENT);
        while (nodeIterator.nextNode()) {
            nodeIterator.referenceNode.remove();
        }
        const dangerousTags = document.querySelectorAll(
            'script, iframe, style, xmp, noembed, noframes, noscript, plaintext, template');
        dangerousTags.forEach(tag => tag.remove());
        const allTags = document.querySelectorAll('*');
        allTags.forEach(tag => {
            const attributes = Array.from(tag.attributes);
            attributes.forEach(attr => tag.removeAttribute(attr.name));
        });
        return document.body.innerHTML;
    } catch (e) {
        console.error("Sanitization failed:", e);
        return "Error processing content.";
    }
}

module.exports = sanitize;
